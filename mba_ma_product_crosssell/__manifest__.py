{
    'name': 'MBA MA - Regla de venta cruzada / Target de productos',
    'version': '18.0.1.0.0',
    'category': 'Marketing/Automation',
    'summary': 'Inscribe clientes que compraron o no compraron productos/categorias especificas',
    'description': """
Regla agnostica de venta cruzada y exclusion de productos/categorias.

Permite segmentar:
* Clientes que compran en general pero NO han comprado un producto o categoria (Exclusion / Cross-selling).
* Clientes que SI han comprado un producto o categoria (Inclusion / Upselling).

La fuente de compras la aporta otro modulo (ej. facturas, ventas, TPV):
* ``crosssell_source`` via ``selection_add``
* metodo ``_crosssell_data_<fuente>(company_ids, min_purchases, product_ids, category_ids, cutoff_date)``
    """,
    'author': 'MBA Consultings',
    'website': 'https://mbaconsultings.com',
    'license': 'AGPL-3',
    'depends': ['mba_ma_enrollment', 'product'],
    'data': ['views/automation_configuration_views.xml'],
    'icon': '/mba_ma_product_crosssell/static/description/icon.png',
    'installable': True,
    'application': False,
}
