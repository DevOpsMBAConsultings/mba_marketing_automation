from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class AutomationConfiguration(models.Model):
    _inherit = 'automation.configuration'

    enrollment_type = fields.Selection(
        selection_add=[('product_crosssell', 'Venta cruzada / Target de productos')],
        ondelete={'product_crosssell': 'set default'},
    )
    crosssell_source = fields.Selection(
        [],
        string='Fuente de compras',
        help="De donde se toman las compras y lineas de productos. La aporta otro modulo.",
    )
    crosssell_mode = fields.Selection(
        [
            ('not_bought', 'Compraron en general pero NO el producto/categoria (Exclusion)'),
            ('has_bought', 'Compraron el producto/categoria (Inclusion)'),
        ],
        string='Modo de coincidencia',
        default='not_bought',
        required=True,
    )
    crosssell_filter_type = fields.Selection(
        [
            ('product', 'Por producto especifico'),
            ('category', 'Por categoria de producto'),
        ],
        string='Filtrar objetivo por',
        default='product',
        required=True,
    )
    crosssell_product_ids = fields.Many2many(
        'product.product',
        'automation_config_product_rel',
        'config_id',
        'product_id',
        string='Productos objetivo',
    )
    crosssell_category_ids = fields.Many2many(
        'product.category',
        'automation_config_category_rel',
        'config_id',
        'category_id',
        string='Categorias objetivo',
    )
    crosssell_lookback_days = fields.Integer(
        string='Ventana de compras (dias)',
        default=0,
        help="Evalua compras realizadas en los ultimos N dias. 0 = historico completo sin limite.",
    )
    crosssell_min_purchases = fields.Integer(
        string='Compras minimas previas',
        default=1,
        help="Minimo de compras generales que el cliente debe tener.",
    )
    crosssell_require_email = fields.Boolean(
        string='Solo con correo',
        default=True,
    )
    crosssell_extra_domain = fields.Char(
        string='Filtro adicional (contactos)',
        default='[]',
        help="Dominio extra sobre contactos, por ejemplo [('customer_rank', '>', 0)].",
    )

    @api.depends(
        'crosssell_source', 'crosssell_mode', 'crosssell_filter_type',
        'crosssell_product_ids', 'crosssell_category_ids',
        'crosssell_lookback_days', 'crosssell_min_purchases',
        'crosssell_require_email', 'crosssell_extra_domain', 'company_id',
    )
    def _compute_domain(self):
        return super()._compute_domain()

    @api.constrains(
        'enrollment_type', 'crosssell_source', 'crosssell_mode',
        'crosssell_filter_type', 'crosssell_product_ids', 'crosssell_category_ids',
        'crosssell_min_purchases', 'crosssell_extra_domain', 'model_id',
    )
    def _check_crosssell_values(self):
        for record in self.filtered(lambda r: r.enrollment_type == 'product_crosssell'):
            if not record.crosssell_source:
                raise ValidationError(_(
                    "Elige una fuente de compras. Si no hay ninguna disponible, "
                    "instala un modulo de fuente (por ejemplo mba_ma_product_crosssell_account)."
                ))
            if record.crosssell_filter_type == 'product' and not record.crosssell_product_ids:
                raise ValidationError(_("Debes seleccionar al menos un producto objetivo."))
            if record.crosssell_filter_type == 'category' and not record.crosssell_category_ids:
                raise ValidationError(_("Debes seleccionar al menos una categoria objetivo."))
            if record.crosssell_min_purchases < 1:
                raise ValidationError(_("Las compras minimas deben ser al menos 1."))
            if record.model_id and record.model_id.model != 'res.partner':
                raise ValidationError(_(
                    "La regla de venta cruzada solo aplica al modelo Contacto (res.partner)."
                ))
            try:
                safe_eval(record.crosssell_extra_domain or '[]', record._get_eval_context())
            except Exception as exc:
                raise ValidationError(_("Filtro adicional invalido: %s") % exc) from exc

    @api.onchange('enrollment_type')
    def _onchange_enrollment_type_crosssell(self):
        if self.enrollment_type == 'product_crosssell':
            self.model_id = self.env['ir.model']._get('res.partner')
            self.filter_id = False
            if not self.crosssell_source:
                options = self._fields['crosssell_source'].get_description(self.env)['selection']
                if options:
                    self.crosssell_source = options[0][0]

    def _enrollment_domain_product_crosssell(self):
        self.ensure_one()
        method = getattr(self, '_crosssell_data_%s' % self.crosssell_source, None)
        if method is None:
            raise UserError(_("La fuente de compras para venta cruzada no esta instalada."))

        company_ids = self.company_id.ids or self.env.companies.ids
        cutoff_date = False
        if self.crosssell_lookback_days > 0:
            today = fields.Date.context_today(self)
            cutoff_date = today - timedelta(days=self.crosssell_lookback_days)

        product_ids = self.crosssell_product_ids.ids if self.crosssell_filter_type == 'product' else []
        category_ids = []
        if self.crosssell_filter_type == 'category' and self.crosssell_category_ids:
            category_ids = self.env['product.category'].search([
                ('id', 'child_of', self.crosssell_category_ids.ids)
            ]).ids

        all_buyers, target_buyers = method(
            company_ids=company_ids,
            min_purchases=self.crosssell_min_purchases,
            product_ids=product_ids,
            category_ids=category_ids,
            cutoff_date=cutoff_date,
        )

        all_buyers_set = set(all_buyers)
        target_buyers_set = set(target_buyers)

        if self.crosssell_mode == 'not_bought':
            qualifying_partner_ids = list(all_buyers_set - target_buyers_set)
        else:
            qualifying_partner_ids = list(target_buyers_set)

        domain = [('id', 'in', qualifying_partner_ids)]
        if self.crosssell_require_email:
            domain.append(('email', '!=', False))
        extra = safe_eval(self.crosssell_extra_domain or '[]', self._get_eval_context())
        return domain + list(extra)
