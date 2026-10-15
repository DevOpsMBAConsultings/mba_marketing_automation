from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class AutomationConfiguration(models.Model):
    _inherit = 'automation.configuration'

    enrollment_type = fields.Selection(
        [('filter', 'Filtro')],
        string='Tipo de inscripcion',
        default='filter',
        required=True,
        help="Filtro: dominio manual (comportamiento original de automation_oca). "
             "Otros tipos los agregan modulos de regla.",
    )
    enrollment_count = fields.Integer(
        string='Registros que cumplen',
        compute='_compute_enrollment_count',
    )

    # Los modulos de regla agregan aqui sus campos con su propio @api.depends:
    # Odoo suma las dependencias de todas las sobreescrituras.
    @api.depends('enrollment_type')
    def _compute_domain(self):
        super()._compute_domain()
        for record in self.filtered(lambda r: r.enrollment_type != 'filter'):
            record.domain = str(record._get_enrollment_domain())

    @api.depends('domain', 'model_id')
    def _compute_enrollment_count(self):
        for record in self:
            count = 0
            if record.model_id and record.domain:
                try:
                    domain = safe_eval(record.domain, record._get_eval_context())
                    count = self.env[record.model_id.model].search_count(domain)
                except Exception:  # noqa: BLE001 - dominio incompleto en edicion
                    count = 0
            record.enrollment_count = count

    def _get_enrollment_domain(self):
        """Despacha a ``_enrollment_domain_<tipo>`` del modulo de la regla."""
        self.ensure_one()
        method = getattr(self, '_enrollment_domain_%s' % self.enrollment_type, None)
        if method is None:
            raise UserError(_(
                "El tipo de inscripcion '%s' no tiene regla instalada.",
                self.enrollment_type,
            ))
        return method()

    def action_view_enrollment_candidates(self):
        self.ensure_one()
        domain = safe_eval(self.domain, self._get_eval_context())
        return {
            'type': 'ir.actions.act_window',
            'name': _('Registros que cumplen la regla'),
            'res_model': self.model_id.model,
            'view_mode': 'list,form',
            'domain': domain,
        }
