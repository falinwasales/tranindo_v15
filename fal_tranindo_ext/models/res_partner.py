from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_market = fields.Char(string="Market")
    partner_wilayah = fields.Char(string="Wilayah")