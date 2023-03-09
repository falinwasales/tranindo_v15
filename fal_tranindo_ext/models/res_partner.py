from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_market = fields.Char(string="Market")
    partner_wilayah = fields.Char(string="Wilayah")

    def _get_current_compnay(self):
        return self.env.company

    company_id = fields.Many2one('res.company', 'Company', index=True, default=_get_current_compnay)