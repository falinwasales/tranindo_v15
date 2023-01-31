{
    'name': 'Falinwa Tranindo Extention',
    'version': '15.0.1.0.0',
    'author': 'Falinwa Limited',
    'summary': 'Module to handle tranindo extention from falinwa',
    'category': 'Falinwa Tranindo Extention',
    'website': "https://falinwa.com",
    'description':
    '''
        Module to handle tranindo extention from falinwa
    ''',
    'depends': ['fal_tranindo_ext','stock_account'],
    'data': [
        'views/stock_valuation_layer_views.xml',
        'security/ir_server_action.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}