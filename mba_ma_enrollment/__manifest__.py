{
    'name': 'MBA MA - Enrollment (nucleo)',
    'version': '18.0.1.0.0',
    'category': 'Marketing/Automation',
    'summary': 'Tipos de inscripcion enchufables para automation_oca, con conteo en vivo',
    'description': """
Nucleo agnostico. No conoce clientes, facturas ni ventas.

Agrega a automation_oca un "Tipo de inscripcion" extensible y un conteo en vivo
de registros que cumplen la regla. Cada regla vive en su propio modulo y se
registra con dos piezas:

* ``enrollment_type`` via ``selection_add``
* un metodo ``_enrollment_domain_<tipo>()`` que devuelve un dominio de Odoo
    """,
    'author': 'MBA Consultings',
    'website': 'https://mbaconsultings.com',
    'license': 'AGPL-3',
    'depends': ['automation_oca'],
    'data': ['views/automation_configuration_views.xml'],
    'icon': '/mba_ma_enrollment/static/description/icon.png',
    'installable': True,
    'application': False,
}
