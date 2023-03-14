from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import logging
import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class StockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    account_id = fields.Many2one('account.account', 'Account', domain=[('deprecated', '=', False)])

    @api.onchange('product_id')
    def onchange_product_id(self):
        coa_account = self.env['account.account'].search([('code','=','5-100-001')])

        self.name = self.product_id.name or ''
        self.split_method = self.product_id.product_tmpl_id.split_method_landed_cost or self.split_method or 'equal'
        self.price_unit = self.product_id.standard_price or 0.0
        accounts_data = self.product_id.product_tmpl_id.get_product_accounts()
        self.account_id = coa_account.id if (self.product_id and coa_account) else accounts_data['stock_input']