from odoo import fields, models


class AutomationConfiguration(models.Model):
    _inherit = 'automation.configuration'

    crosssell_source = fields.Selection(
        selection_add=[('invoice', 'Facturas de cliente publicadas')],
        ondelete={'invoice': 'set null'},
    )

    def _crosssell_data_invoice(self, company_ids, min_purchases, product_ids, category_ids, cutoff_date):
        """
        Retorna (all_buyers, target_buyers) a partir de facturas de clientes publicadas.
        all_buyers: commercial_partner_id con al menos min_purchases facturas publicadas.
        target_buyers: commercial_partner_id con facturas publicadas que contienen los productos/categorias.
        """
        company_ids_list = list(company_ids)

        # 1. Compradores generales (con minimo de compras en facturas)
        base_query = """
            SELECT commercial_partner_id
              FROM account_move
             WHERE move_type = 'out_invoice'
               AND state = 'posted'
               AND commercial_partner_id IS NOT NULL
               AND company_id = ANY(%s)
        """
        params = [company_ids_list]
        if cutoff_date:
            base_query += " AND invoice_date >= %s"
            params.append(cutoff_date)
        base_query += " GROUP BY commercial_partner_id HAVING COUNT(DISTINCT id) >= %s"
        params.append(min_purchases)

        self.env.cr.execute(base_query, params)
        all_buyers = [row[0] for row in self.env.cr.fetchall()]

        # 2. Compradores de los productos o categorias objetivo
        target_buyers = []
        if product_ids or category_ids:
            target_query = """
                SELECT DISTINCT m.commercial_partner_id
                  FROM account_move_line l
                  JOIN account_move m ON l.move_id = m.id
                  JOIN product_product p ON l.product_id = p.id
                  JOIN product_template t ON p.product_tmpl_id = t.id
                 WHERE m.move_type = 'out_invoice'
                   AND m.state = 'posted'
                   AND m.commercial_partner_id IS NOT NULL
                   AND m.company_id = ANY(%s)
            """
            target_params = [company_ids_list]
            if cutoff_date:
                target_query += " AND m.invoice_date >= %s"
                target_params.append(cutoff_date)

            if product_ids:
                target_query += " AND l.product_id = ANY(%s)"
                target_params.append(list(product_ids))
            elif category_ids:
                target_query += " AND t.categ_id = ANY(%s)"
                target_params.append(list(category_ids))

            self.env.cr.execute(target_query, target_params)
            target_buyers = [row[0] for row in self.env.cr.fetchall()]

        return all_buyers, target_buyers
