# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'Falinwa Tranindo Email Invoice Faktur',
    'version': '12.0.1.0.0',
    'author': 'Falinwa Limited',
    'summary': 'Module to handle tranindo extention from falinwa',
    'category': 'Sale',
    'website': "https://falinwa.com",
    'description':
    '''
        Module to handle tranindo invoice email
    ''',
    'depends': [
        'sale_stock',
        'account',
        'base',
        'mail',
        'contacts',
        'fal_tranindo_ext',
    ],
    'data': [
        'views/customer_type_views.xml',
        'views/account_move_views.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'views/faktur_email_template.xml',
        'security/ir.model.access.csv',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
