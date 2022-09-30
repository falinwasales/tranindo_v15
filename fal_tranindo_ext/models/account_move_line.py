import time
import math
from odoo import models, fields, api
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.tools.translate import _
from odoo.tools import append_content_to_html, DEFAULT_SERVER_DATE_FORMAT, html2plaintext
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    follow_block = fields.Boolean(string="Booean Field", default=False)
    
    blocked = fields.Boolean(string='No Follow-up', readonly=False,
        help="You can check this box to mark this journal item as a litigation with the associated partner")

    disc_round = fields.Float(string="Disc Round", compute="_round_discount")

    @api.depends('discount')
    def _round_discount(self):
        for record in self:
            if int(repr(record.discount)[-1]) == 5:
                record.disc_round = math.ceil(record.discount * 100)/100
            else:
                record.disc_round = round(record.discount,2)

    @api.onchange(fields.Date.today())
    def _get_value(self):
        for record in self:
            today = fields.Date.today()
            if today > record.date_maturity:
                record.blocked = True
            else:
                record.blocked = False