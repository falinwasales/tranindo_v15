# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
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
    'depends': [
        'base',
        'sale',
        'sale_stock',
        'sales_team',
        'account',
        'account_reports',
        'stock',
        'purchase',
        'point_of_sale',
        'base_automation',
        # 'report',
    ],
    'data': [
        # Form File
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/res_company_views.xml',
        'views/stock_picking_views.xml',
        'views/purchase_order_view.xml',
        'views/point_of_sale_views.xml',
        'views/res_partner_views.xml',
        'views/report_followup_views.xml',
        'views/tanda_terima_views.xml',
        'views/report_invoice_views.xml',
        'views/report_sale_order_views.xml',
        'views/stock_quant_views.xml',
        'views/stock_move_line_views.xml',
        # Wizard Form
        'wizard/stock_cancel_option_views.xml',
        # Report File
        'report/tranindo_report_sj_transfer_header_footer.xml',
        'report/tranindo_report_sj_letter_header_footer.xml',
        'report/tranindo_voucher_a4_header_footer.xml',
        'report/tranindo_voucher_c5_header_footer.xml',
        'report/tranindo_invoice_letter_header_footer.xml',
        'report/tranindo_invoice_letter_c5_header_footer.xml',
        'report/tranindo_vendor_bill_c5_header_footer.xml',
        'report/tranindo_vendor_bill_a4_header_footer.xml',
        'report/tranindo_rpj_c5_header_footer.xml',
        # 'report/layouts.xml',
        'report/invoice_letter.xml',
        'report/invoice_letter_c5.xml',
        'report/sj_transfers_c5.xml',
        'report/sj_letters_c5.xml',
        'report/voucher_c5.xml',
        'report/voucher_a4.xml',
        'report/rpj_c5.xml',
        'report/vendor_bill_c5.xml',
        'report/vendor_bill_a4.xml',
        'report/sticker.xml',
        'report/tranindo_sticker_header_footer.xml',
        'report/tanda_terima_A4.xml',
        'report/tanda_terima_header_footer_A4.xml',
        'report/tanda_terima_C5.xml',
        'report/tanda_terima_header_footer_C5.xml',
        'report/sale_order_report/sale_order_report.xml',
        'report/sale_order_report/sale_order_report_header.xml',
        # Security
        'security/ir_server_action.xml',
        'security/ir.model.access.csv',
        'security/ir_cron_action.xml',
        # Data
        'data/sequence.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
