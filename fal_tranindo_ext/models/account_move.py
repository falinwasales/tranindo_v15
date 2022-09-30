from odoo import _, exceptions, fields, models, api
import datetime
from dateutil.relativedelta import relativedelta, MO, SU
from odoo.exceptions import UserError, ValidationError
from num2words import num2words


class AccountInvoice(models.Model):
    _inherit = "account.move"

    replace_faktur = fields.Char(string="Replace Tax")

    fal_stock_picking_id = fields.Many2one("stock.picking", string="Delivery", compute='_fal_get_stock_picking')
    date_invoice = fields.Date(string='Date Invoices')
    payment_voucher_bool = fields.Boolean(string="Payment Voucher")
    is_delivery_address = fields.Boolean(string="Delivery Address", help="Apabila dichecklist, maka akan mengambil delivery address di account.move")
    credit_note = fields.Boolean(string="Credit Note")

    customer_npwp = fields.Char(string="NPWP")
    customer_pkp = fields.Boolean(string="Customer PKP")
    invoice_salesperson = fields.Many2one(string="Salesperson", related="fal_stock_picking_id.sale_id.user_id")

    after_date = fields.Date(string="After Due Date Custom")
    invoice_payment_state = fields.Char(string="Test")

    tt_id = fields.Many2one("tanda.terima", string="Tanda Terima ID")
    tt_tax_get = fields.Char(string="Tax Container", compute="_get_tax_value")

    tt_nomor_id = fields.Many2one("tanda.terima", string="Nomor Tanda Terima")
    tt_date = fields.Date(string="Tanggal Tanda Terima", related="tt_nomor_id.tanda_terima_date")
    tt_bool = fields.Boolean(string="Bool Tanda Terima", default=False)

    sale_final_bool = fields.Boolean(string="Sale final bool", related="fal_stock_picking_id.sale_id.is_final_customer")

    pos_comission_id = fields.Many2one("pos.order", string="PoS ID")

    def _get_tax_value(self):
        for record in self:
            record.tt_tax_get = ""
            if record.replace_faktur:
                record.tt_tax_get = record.replace_faktur
            elif record.l10n_id_tax_number:
                record.tt_tax_get = record.l10n_id_tax_number
            else:
                record.tt_tax_get = ""

            
    
    def get_amount_to_text(self, total_amount):
        return num2words(total_amount, lang="id")

    html_word = fields.Char(string="HTML Word", compute="_html_to_word")

    @api.depends("narration")
    def _html_to_word(self):
        for record in self:
            text = ""
            word = ['<p>','</p>','<b>','</b>','<h1>','</h1>']

            if record.narration:
                for banned in word:
                    text = record.narration.replace(banned, "")
            
            print(text)
            
            record.html_word = text
    
    @api.depends('invoice_line_ids')
    def _fal_get_stock_picking(self):
        for invoice in self:
            sale_order_ids = invoice.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
            if sale_order_ids:
                invoice.fal_stock_picking_id = sale_order_ids[0].fal_stock_picking_id.id if sale_order_ids[0].fal_stock_picking_id else False
            else:
                invoice.fal_stock_picking_id = ''

    fal_paid_date = fields.Date(string='Paid Date')
    fal_payment_method = fields.Many2one('account.journal', string='Payment Method')
    

