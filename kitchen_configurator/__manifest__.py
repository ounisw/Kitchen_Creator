{
    'name': 'Kitchen & Wardrobe Configurator 3D',
    'version': '19.0.1.3.0',
    'category': 'Sales/Sales',
    'summary': '3D kitchen and wardrobe configurator with technical drawing, linked to quotations',
    'description': """
Design kitchens and wardrobes in 3D inside Odoo, print the dimensioned technical drawing and
create the quotation lines in one click. For salespeople (from the quotation) and portal customers.
""",
    'author': 'Classic Decoration',
    'maintainer': 'Classic Decoration',
    'depends': ['sale', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'security/kitchen_security.xml',
        'data/product_data.xml',
        'views/kitchen_design_views.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'views/portal_templates.xml',
        'report/kitchen_drawing_report.xml',
    ],
    'installable': True,
    'application': False,
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
}
