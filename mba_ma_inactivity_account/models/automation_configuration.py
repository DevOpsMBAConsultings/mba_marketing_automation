from odoo import fields, models


class AutomationConfiguration(models.Model):
    _inherit = 'automation.configuration'

    inactivity_source = fields.Selection(
        selection_add=[('invoice', 'Facturas de cliente publicadas')],
        ondelete={'invoice': 'set null'},
    )

    def _inactivity_rows_invoice(self, company_ids):
        """(empresa, ultima fecha de factura, cantidad) por empresa comercial."""
        self.env.cr.execute("""
            SELECT commercial_partner_id, MAX(invoice_date), COUNT(*)
              FROM account_move
             WHERE move_type = 'out_invoice'
               AND state = 'posted'
               AND commercial_partner_id IS NOT NULL
               AND company_id = ANY(%s)
             GROUP BY commercial_partner_id
        """, [list(company_ids)])
        return self.env.cr.fetchall()
