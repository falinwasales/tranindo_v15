from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import logging
import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class StockBom(models.Model):
    _name = 'stock.bom'

    product_id = fields.Many2one('product.product', string="Product")
    bom_product_qty = fields.Float(string="On Hand Quantity")
    bom_qty = fields.Float(string="Demand")
    product_uom = fields.Many2one('uom.uom', string="Product Uom")
    picking_id = fields.Many2one('stock.picking', string="Picking ID")