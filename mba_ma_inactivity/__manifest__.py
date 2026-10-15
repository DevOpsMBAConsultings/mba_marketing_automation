{
    'name': 'MBA MA - Regla de cliente inactivo',
    'version': '19.0.1.0.0',
    'category': 'Marketing/Automation',
    'summary': 'Inscribe empresas que ya compraron y llevan N dias sin comprar (fuente enchufable)',
    'description': """
Regla "cliente inactivo", agnostica de donde vienen las compras.

La fuente de actividad la aporta otro modulo (facturas, ventas, TPV...):

* ``inactivity_source`` via ``selection_add``
* un metodo ``_inactivity_rows_<fuente>(company_ids)`` que devuelve una lista
  de tuplas ``(partner_id, ultima_fecha, cantidad)`` por empresa.

Sin ninguna fuente instalada la regla no se puede usar.
    """,
    'author': 'MBA Consultings',
    'website': 'https://mbaconsultings.com',
    'license': 'AGPL-3',
    'depends': ['mba_ma_enrollment'],
    'data': ['views/automation_configuration_views.xml'],
    'icon': '/mba_ma_inactivity/static/description/icon.png',
    'installable': True,
    'application': False,
}
