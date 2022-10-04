from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import logging
import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = "stock.move"

    move_product_uom_qty = fields.Float(string="On hand Qty", related="product_id.qty_available")


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    line_product_uom_qty = fields.Float(string="On hand Qty Qty", related="product_id.qty_available")
    product_uom_qty = fields.Float(
        'Reserved', default=0.0, digits='Product Unit of Measure', required=True)