{
    'name': "Gestion Profesorado",
    'summary': "Módulo para la gestión de profesores",
    'description': """
        Módulo básico para la gestión de profesorado en Odoo 18.
    """,
    'author': "Kaazest",
    'website': "https://www.yourcompany.com",
    'category': 'Education',
    'version': '18.0.1.0.0',
    'depends': ['base', 'website', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/teacher_views.xml',
        'views/activity_views.xml',
        'security/security_rules.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
