from odoo import _, exceptions, fields, models, api
import datetime
from dateutil.relativedelta import relativedelta, MO, SU
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from odoo.tools import float_round, date_utils
import math
import json

FK_HEAD_LIST = ['FK', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR', 'MASA_PAJAK', 'TAHUN_PAJAK', 'TANGGAL_FAKTUR', 'NPWP', 'NAMA', 'ALAMAT_LENGKAP', 'JUMLAH_DPP', 'JUMLAH_PPN', 'JUMLAH_PPNBM', 'ID_KETERANGAN_TAMBAHAN', 'FG_UANG_MUKA', 'UANG_MUKA_DPP', 'UANG_MUKA_PPN', 'UANG_MUKA_PPNBM', 'REFERENSI', 'KODE_DOKUMEN_PENDUKUNG']

LT_HEAD_LIST = ['LT', 'NPWP', 'NAMA', 'JALAN', 'BLOK', 'NOMOR', 'RT', 'RW', 'KECAMATAN', 'KELURAHAN', 'KABUPATEN', 'PROPINSI', 'KODE_POS', 'NOMOR_TELEPON']

OF_HEAD_LIST = ['OF', 'KODE_OBJEK', 'NAMA', 'HARGA_SATUAN', 'JUMLAH_BARANG', 'HARGA_TOTAL', 'DISKON', 'DPP', 'PPN', 'TARIF_PPNBM', 'PPNBM']

def _csv_row(data, delimiter=',', quote='"'):
    return quote + (quote + delimiter + quote).join([str(x).replace(quote, '\\' + quote) for x in data]) + quote + '\n'


class AccountInvoice(models.Model):
    _inherit = "account.move"

    replace_faktur = fields.Char(string="Replace Tax")

    fal_stock_picking_id = fields.Many2one("stock.picking", string="Delivery", compute='_fal_get_stock_picking')
    date_invoice = fields.Date(string='Date Invoices')
    payment_voucher_bool = fields.Boolean(string="Payment Voucher")
    is_delivery_address = fields.Boolean(string="Delivery Address", help="Apabila dichecklist, maka akan mengambil delivery address di account.move")
    credit_note = fields.Boolean(string="Credit Note")

    customer_npwp = fields.Char(string="NPWP", related="partner_id.vat")
    customer_pkp = fields.Boolean(string="Customer PKP", related="partner_id.l10n_id_pkp")
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

    payment_memo = fields.Char(string="Payment Memo", compute="_get_memo_from_payment")

    def _get_memo_from_payment(self):
        for record in self:
            record.payment_memo = ''
            search_payment = self.env['account.payment'].search([("ref","ilike",record.name)],limit=1)
            if search_payment:
                record.payment_memo = '%s(%s)' % (search_payment.journal_id.name, search_payment.ref)


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
    
    def _generate_efaktur_invoice(self, delimiter):
        """Generate E-Faktur for customer invoice."""
        # Invoice of Customer
        company_id = self.company_id
        dp_product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')

        output_head = '%s%s%s' % (
            _csv_row(FK_HEAD_LIST, delimiter),
            _csv_row(LT_HEAD_LIST, delimiter),
            _csv_row(OF_HEAD_LIST, delimiter),
        )

        for move in self.filtered(lambda m: m.state == 'posted'):
            eTax = move._prepare_etax()

            nik = str(move.partner_id.l10n_id_nik) if not move.partner_id.vat else ''

            if move.l10n_id_replace_invoice_id:
                number_ref = str(move.l10n_id_replace_invoice_id.name) + " replaced by " + str(move.name)
            else:
                number_ref = str(move.name)

            street = ', '.join([x for x in (move.partner_id.street, move.partner_id.street2) if x])

            invoice_npwp = '000000000000000'
            if move.partner_id.vat and len(move.partner_id.vat) >= 12:
                invoice_npwp = move.partner_id.vat
            elif (not move.partner_id.vat or len(move.partner_id.vat) < 12) and move.partner_id.l10n_id_nik:
                invoice_npwp = move.partner_id.l10n_id_nik
            invoice_npwp = invoice_npwp.replace('.', '').replace('-', '')

            jumlah_dpp = 0
            jumlah_ppn = 0

            for line in move.line_ids.filtered(lambda l: not l.exclude_from_invoice_tab and not l.display_type):
                invoice_line_unit_price = line.price_unit

                invoice_line_total_price = invoice_line_unit_price * line.quantity
                harga_total = invoice_line_total_price / (100/100 + (line.tax_ids.amount/100)) if line.tax_ids.price_include else invoice_line_total_price
                discount_value = harga_total * line.discount/100
                dpp_amount = harga_total - discount_value
                ppn_amount = (harga_total - discount_value) * line.tax_ids.amount/100

                # harga_total_round = math.ceil(harga_total) if (harga_total%1) >= 0.44 else math.floor(harga_total)
                # discount_value_round = math.ceil(discount_value) if (discount_value%1) >= 0.44 else math.floor(discount_value)
                jumlah_dpp += math.ceil(dpp_amount) if (dpp_amount%1) >= 0.44 else math.floor(dpp_amount)
                jumlah_ppn += math.ceil(ppn_amount) if (ppn_amount%1) >= 0.44 else math.floor(ppn_amount)
            

            # Here all fields or columns based on eTax Invoice Third Party
            eTax['KD_JENIS_TRANSAKSI'] = move.l10n_id_tax_number[0:2] or 0
            eTax['FG_PENGGANTI'] = move.l10n_id_tax_number[2:3] or 0
            eTax['NOMOR_FAKTUR'] = move.l10n_id_tax_number[3:] or 0
            eTax['MASA_PAJAK'] = move.invoice_date.month
            eTax['TAHUN_PAJAK'] = move.invoice_date.year
            eTax['TANGGAL_FAKTUR'] = '{0}/{1}/{2}'.format(move.invoice_date.day, move.invoice_date.month, move.invoice_date.year)
            eTax['NPWP'] = invoice_npwp
            eTax['NAMA'] = move.partner_id.name if eTax['NPWP'] == '000000000000000' else move.partner_id.l10n_id_tax_name or move.partner_id.name
            eTax['ALAMAT_LENGKAP'] = move.partner_id.contact_address.replace('\n', '') if eTax['NPWP'] == '000000000000000' else move.partner_id.l10n_id_tax_address or street
            eTax['JUMLAH_DPP'] = jumlah_dpp # currency rounded to the unit
            eTax['JUMLAH_PPN'] = jumlah_ppn
            eTax['ID_KETERANGAN_TAMBAHAN'] = '1' if move.l10n_id_kode_transaksi == '07' else ''
            eTax['REFERENSI'] = number_ref
            eTax['KODE_DOKUMEN_PENDUKUNG'] = '0'

            lines = move.line_ids.filtered(lambda x: x.product_id.id == int(dp_product_id) and x.price_unit < 0 and not x.display_type)
            eTax['FG_UANG_MUKA'] = 0
            eTax['UANG_MUKA_DPP'] = int(abs(sum(lines.mapped(lambda l: float_round(l.price_subtotal, 0)))))
            eTax['UANG_MUKA_PPN'] = int(abs(sum(lines.mapped(lambda l: float_round(l.price_total - l.price_subtotal, 0)))))

            fk_values_list = ['FK'] + [eTax[f] for f in FK_HEAD_LIST[1:]]

            # HOW TO ADD 2 line to 1 line for free product
            free, sales = [], []

            for line in move.line_ids.filtered(lambda l: not l.exclude_from_invoice_tab and not l.display_type):
                # *invoice_line_unit_price is price unit use for harga_satuan's column
                # *invoice_line_quantity is quantity use for jumlah_barang's column
                # *invoice_line_total_price is bruto price use for harga_total's column
                # *invoice_line_discount_m2m is discount price use for diskon's column
                # *line.price_subtotal is subtotal price use for dpp's column
                # *tax_line or free_tax_line is tax price use for ppn's column
                free_tax_line = tax_line = bruto_total = total_discount = 0.0

                for tax in line.tax_ids:
                    if tax.amount > 0:
                        tax_line += line.price_subtotal * (tax.amount / 100.0)

                invoice_line_unit_price = line.price_unit

                invoice_line_total_price = invoice_line_unit_price * line.quantity
                harga_total = invoice_line_total_price / (100/100 + (line.tax_ids.amount/100)) if line.tax_ids.price_include else invoice_line_total_price
                discount_value = harga_total * line.discount/100
                dpp_amount = harga_total - discount_value
                ppn_amount = (harga_total - discount_value) * line.tax_ids.amount/100

                harga_total_round = math.ceil(harga_total) if (harga_total%1) >= 0.44 else math.floor(harga_total)
                discount_value_round = math.ceil(discount_value) if (discount_value%1) >= 0.44 else math.floor(discount_value)
                dpp_amount_round = math.ceil(dpp_amount) if (dpp_amount%1) >= 0.44 else math.floor(dpp_amount)
                ppn_amount_round = math.ceil(ppn_amount) if (ppn_amount%1) >= 0.44 else math.floor(ppn_amount)

                line_dict = {
                    'KODE_OBJEK': line.product_id.default_code or '',
                    # 'NAMA': '[%s] %s'%(line.product_id.default_code, line.product_id.name) if line.product_id.default_code else line.product_id.name or '',
                    'NAMA': line.name,
                    'HARGA_SATUAN': int(float_round(invoice_line_unit_price, 0)),
                    'JUMLAH_BARANG': line.quantity,
                    'HARGA_TOTAL': harga_total_round,
                    'DPP': dpp_amount_round,
                    'product_id': line.product_id.id,
                }

                if line.price_subtotal < 0:
                    for tax in line.tax_ids:
                        free_tax_line += (line.price_subtotal * (tax.amount / 100.0)) * -1.0

                    line_dict.update({
                        'DISKON': discount_value_round,
                        'PPN': ppn_amount_round,
                    })
                    free.append(line_dict)
                elif line.price_subtotal != 0.0 or line.price_subtotal == 0:
                    invoice_line_discount_m2m = invoice_line_total_price - line.price_subtotal

                    line_dict.update({
                        'DISKON': discount_value_round,
                        'PPN': ppn_amount_round,
                    })
                    sales.append(line_dict)

            sub_total_before_adjustment = sub_total_ppn_before_adjustment = 0.0

            # We are finding the product that has affected
            # by free product to adjustment the calculation
            # of discount and subtotal.
            # - the price total of free product will be
            # included as a discount to related of product.
            for sale in sales:
                for f in free:
                    if f['product_id'] == sale['product_id']:
                        sale['DISKON'] = sale['DISKON'] - f['DISKON'] + f['PPN']
                        sale['DPP'] = sale['DPP'] + f['DPP']

                        tax_line = 0

                        for tax in line.tax_ids:
                            if tax.amount > 0:
                                tax_line += sale['DPP'] * (tax.amount / 100.0)

                        sale['PPN'] = int(float_round(tax_line, 0))

                        free.remove(f)

                sub_total_before_adjustment += sale['DPP']
                sub_total_ppn_before_adjustment += sale['PPN']
                bruto_total += sale['DISKON']
                total_discount += float_round(sale['DISKON'], 2)

            output_head += _csv_row(fk_values_list, delimiter)
            for sale in sales:
                of_values_list = ['OF'] + [str(sale[f]) for f in OF_HEAD_LIST[1:-2]] + ['0', '0']
                output_head += _csv_row(of_values_list, delimiter)

        return output_head

