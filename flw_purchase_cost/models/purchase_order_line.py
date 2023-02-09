from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # product_cost = fields.Float(string="Product Cost", related="product_id.standard_price")
    standard_price = fields.Float(string="Product Cost", store=True, compute="_onchange_product_standard_price")


    @api.depends('product_id')
    def _onchange_product_standard_price(self):
        for record in self:
            record.standard_price = 0
            if record.product_id:
                record.standard_price = record.product_id.standard_price