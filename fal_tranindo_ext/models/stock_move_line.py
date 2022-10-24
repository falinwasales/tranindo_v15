from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import logging
import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = "stock.move"

    move_product_uom_qty = fields.Float(string="On hand Qty", compute="_get_qty_location")
    product_move_bom = fields.Many2one('product.product', string="Product BoM", compute="_get_bom_product")
    product_move_bom_internal = fields.Many2one('product.product',string="Product BoM")

    @api.onchange('product_id')
    def _onchange_product_id_get_bom(self):
        for record in self:
            product = record.product_id.with_context(lang=self._get_lang())
            if product:
                record.product_move_bom_internal = product.id

    @api.depends('product_id')
    def _get_bom_product(self):
        for record in self:
            record.product_move_bom = False
            if record.sale_line_id:
                for sale_id in record.sale_line_id:
                    record.product_move_bom = sale_id.product_id


    @api.depends('location_id')
    def _get_qty_location(self):
        for record in self:
            qty = 0
            ware = record.location_id
            quant = self.env['stock.quant'].search([('product_id','=',record.product_id.id),('location_id','=',ware.id)])
            if quant:
                qty = quant.quantity
                record.move_product_uom_qty = qty
            else:
                record.move_product_uom_qty = 0

    @api.onchange('product_id')
    def _get_qty_location_onchange(self):
        for record in self:
            qty = 0
            ware = record.location_id
            quant = self.env['stock.quant'].search([('product_id','=',record.product_id.id),('location_id','=',ware.id)])
            if quant:
                qty = quant.quantity
                record.move_product_uom_qty = qty
            else:
                record.move_product_uom_qty = 0


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    line_product_uom_qty = fields.Float(string="On hand Qty", compute="_get_qty_location")
    # product_uom_qty = fields.Float(
    #     'Reserved', default=0.0, digits='Product Unit of Measure', required=True)

    @api.depends('location_id')
    def _get_qty_location(self):
        for record in self:
            qty = 0
            ware = record.location_id
            quant = self.env['stock.quant'].search([('product_id','=',record.product_id.id),('location_id','=',ware.id)])
            if quant:
                qty = quant.quantity
                record.line_product_uom_qty = qty
            else:
                record.line_product_uom_qty = 0

    @api.onchange('product_id')
    def _get_qty_location_onchange(self):
        for record in self:
            qty = 0
            ware = record.location_id
            quant = self.env['stock.quant'].search([('product_id','=',record.product_id.id),('location_id','=',ware.id)])
            if quant:
                qty = quant.quantity
                record.line_product_uom_qty = qty
            else:
                record.line_product_uom_qty = 0