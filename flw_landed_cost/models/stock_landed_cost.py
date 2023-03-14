from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import logging
import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def _default_account_journal_id(self):
        """Take the journal configured in the company, else fallback on the stock journal."""
        lc_journal = self.env['account.journal']
        lc_journal_default = self.env['account.journal'].search([('code','=','LDC')])

        if lc_journal_default:
            return lc_journal_default
        else:
            if self.env.company.lc_journal_id:
                lc_journal = self.env.company.lc_journal_id
            else:
                lc_journal = self.env['ir.property']._get("property_stock_journal", "product.category")
            return lc_journal