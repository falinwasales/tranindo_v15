import time
from odoo import models, fields, api
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.tools.translate import _
from odoo.tools import append_content_to_html, DEFAULT_SERVER_DATE_FORMAT, html2plaintext
from odoo.exceptions import UserError

class AccountJournal(models.AbstractModel):
    _inherit = "account.journal"

    ir_sequence_return_id = fields.Many2one('ir.sequence', string="Entry Sequence PoS")