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
    'depends': ['base', 'p3base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml'
    ],
}
