{
    'name': 'Product Loan',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Manage product loans',
    'author': 'Your Name',
    'website': 'https://www.yourwebsite.com',
    'license': 'AGPL-3',
    'depends': ['base', 'contacts', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/views.xml',
        'views/product_return_views.xml',
        'reports/templates.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
