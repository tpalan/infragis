{
    'name': "infragis",
    'summary': """
        InfraGIS management""",
    'description': """
        Adds:
	- reference from invoice to partner (for referencing real customer)
    """,
    'author': "Tom Palan <thomas@palan.at>",
    'website': "http://www.palan.at",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'p3base', 'sale_management'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/views_index.xml',
        'views/views_project.xml',
        'views/views_sale_order.xml',
        'views/views_menu.xml'
    ],
}
