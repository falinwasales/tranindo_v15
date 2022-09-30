# -*- coding: utf-8 -*-
{
    "name": "Payment Bank Provision",
    'version': '15.0.1.0.0',
    'license': 'OPL-1',
    'summary': """Payment using cheque.""",
    'category': 'Accounting & Finance',
    'author': "CLuedoo",
    'website': "https://www.cluedoo.com/",
    'support': 'cluedoo@falinwa.com',
    "description": """
        Bank Provision
        =================================

        Payment using cheque
    """,
    "depends": [
        "fal_multi_payment_wizard",
    ],
    "init_xml": [],
    "data": [
        "security/ir.model.access.csv",
        "data/account_data.xml",
        "data/provision_journal_data.xml",
        "views/bank_provision_view.xml",
        "views/account_journal_view.xml",
        "wizard/fal_multi_payment_wizard_view.xml",
    ],
    'images': [
        'static/description/bank_provision_screenshoot.png'
    ],
    'demo': [
    ],
    'price': 720.00,
    'currency': 'EUR',
    'application': False,
}
