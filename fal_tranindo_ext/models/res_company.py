from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    fax = fields.Char(string="Fax")
    invoice_name = fields.Char(string="Invoice Name")
    company_keterangan = fields.Text(string="Keterangan")
    quotation_note = fields.Text(string="Quotation Note")
    invoice_ttd = fields.Char(string="Invoice")
    invoice_sj1 = fields.Char(string="Dikeluarkan Oleh")
    invoice_sj2 = fields.Char(string="Mengetahui")
    invoice_sj3 = fields.Char(string="Dikirim Oleh")
    invoice_sj4 = fields.Char(string="Diterima Oleh")