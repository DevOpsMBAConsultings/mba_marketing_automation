from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class AutomationConfiguration(models.Model):
    _inherit = 'automation.configuration'

    enrollment_type = fields.Selection(
        selection_add=[('inactivity', 'Cliente inactivo')],
        ondelete={'inactivity': 'set default'},
    )
    inactivity_source = fields.Selection(
        [],
        string='Fuente de compras',
        help="De donde se toma la actividad de compra. La aporta otro modulo.",
    )
    inactivity_days = fields.Integer(
        string='Dias sin comprar', default=90,
        help="Se inscribe al cliente si su ultima compra es anterior a hoy menos "
             "estos dias.",
    )
    inactivity_lookback_days = fields.Integer(
        string='Ignorar clientes perdidos tras (dias)', default=365,
        help="Excluye clientes cuya ultima compra es anterior a este limite (ya "
             "perdidos). 0 = sin limite.",
    )
    inactivity_min_purchases = fields.Integer(
        string='Compras minimas previas', default=1,
    )
    inactivity_require_email = fields.Boolean(string='Solo con correo', default=True)
    inactivity_extra_domain = fields.Char(
        string='Filtro adicional (contactos)', default='[]',
        help="Dominio extra sobre contactos, por ejemplo [('customer_rank', '>', 0)].",
    )

    @api.depends(
        'inactivity_source', 'inactivity_days', 'inactivity_lookback_days',
        'inactivity_min_purchases', 'inactivity_require_email',
        'inactivity_extra_domain', 'company_id',
    )
    def _compute_domain(self):
        return super()._compute_domain()

    @api.constrains(
        'enrollment_type', 'inactivity_source', 'inactivity_days',
        'inactivity_lookback_days', 'inactivity_min_purchases',
        'inactivity_extra_domain', 'model_id',
    )
    def _check_inactivity_values(self):
        for record in self.filtered(lambda r: r.enrollment_type == 'inactivity'):
            if not record.inactivity_source:
                raise ValidationError(_(
                    "Elige una fuente de compras. Si no hay ninguna disponible, "
                    "instala un modulo de fuente (por ejemplo "
                    "mba_ma_inactivity_account)."
                ))
            if record.inactivity_days < 1:
                raise ValidationError(_("Los dias sin comprar deben ser al menos 1."))
            if record.inactivity_min_purchases < 1:
                raise ValidationError(_("Las compras minimas deben ser al menos 1."))
            if record.inactivity_lookback_days and (
                record.inactivity_lookback_days <= record.inactivity_days
            ):
                raise ValidationError(_(
                    "El limite de clientes perdidos debe ser mayor que los dias sin comprar."
                ))
            if record.model_id and record.model_id.model != 'res.partner':
                raise ValidationError(_(
                    "La regla de cliente inactivo solo aplica al modelo Contacto."
                ))
            try:
                safe_eval(record.inactivity_extra_domain or '[]',
                          record._get_eval_context())
            except Exception as exc:  # noqa: BLE001
                raise ValidationError(_("Filtro adicional invalido: %s") % exc) from exc

    @api.onchange('enrollment_type')
    def _onchange_enrollment_type_inactivity(self):
        if self.enrollment_type == 'inactivity':
            self.model_id = self.env['ir.model']._get('res.partner')
            self.filter_id = False
            if not self.inactivity_source:
                options = self._fields['inactivity_source'].get_description(
                    self.env)['selection']
                if options:
                    self.inactivity_source = options[0][0]

    def _enrollment_domain_inactivity(self):
        """Dominio sobre res.partner. La fuente solo entrega filas agregadas."""
        self.ensure_one()
        method = getattr(self, '_inactivity_rows_%s' % self.inactivity_source, None)
        if method is None:
            raise UserError(_("La fuente de compras no esta instalada."))
        today = fields.Date.context_today(self)
        cutoff = today - timedelta(days=self.inactivity_days)
        floor = (
            today - timedelta(days=self.inactivity_lookback_days)
            if self.inactivity_lookback_days else False
        )
        company_ids = self.company_id.ids or self.env.companies.ids
        partner_ids = [
            partner_id
            for partner_id, last_date, count in method(company_ids)
            if last_date and last_date < cutoff
            and count >= self.inactivity_min_purchases
            and (not floor or last_date >= floor)
        ]
        domain = [('id', 'in', partner_ids)]
        if self.inactivity_require_email:
            domain.append(('email', '!=', False))
        extra = safe_eval(self.inactivity_extra_domain or '[]',
                          self._get_eval_context())
        return domain + list(extra)
