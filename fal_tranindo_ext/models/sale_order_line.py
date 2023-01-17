from odoo import fields, models, api, _
from odoo.exceptions import UserError
import math
import logging

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    disc_round = fields.Float(string="Disc Round", compute="_round_discount")
    product_qty_available = fields.Float(string="Qty Available", compute="_get_product_uom_warehouse")
    total_delivered = fields.Float(string="Total")

    # def _get_total_done(self):
    #     for record in self:
    #         record.total_delivered = 0
    #         move_line = self.env['stock.picking'].search([('picking_id','in','record.order_id.picking_ids.ids')])
    #         print('999999999')    
    #         print(move_line)

    @api.depends('warehouse_id')
    def _get_product_uom_warehouse(self):
        for record in self:
            ware = record.warehouse_id.lot_stock_id
            quant = self.env['stock.quant'].search([('product_id','=',record.product_id.id),('location_id','=',ware.id)])
            qty = 0
            if quant:
                qty = quant.quantity
                record.product_qty_available = qty
            else:
                record.product_qty_available = 0

    @api.onchange('product_id')
    def _onchange_product_uom_product(self):
        for record in self:
            ware = record.order_id.warehouse_id
            quant = self.env['stock.quant'].search([('product_id','=',record.product_id.id),('location_id','=',ware.lot_stock_id.id)])
            qty = 0
            if quant:
                qty = quant.quantity
                record.product_qty_available = qty
            else:
                record.product_qty_available = 0

    @api.depends('discount')
    def _round_discount(self):
        for record in self:
            if int(repr(record.discount)[-1]) == 5:
                record.disc_round = math.ceil(record.discount * 100)/100
            else:
                record.disc_round = round(record.discount,2)

    @api.onchange('product_id')
    def _warning_onchange_product_qty_on_hand(self):
        for record in self:
            if record.product_id:
                if record.product_qty_available <= 0:
                    warning_mess = {
                        'title': _('Warning.'),
                        'message': _('The product [%s] have 0 Qty on Hand.' % (record.product_id.name))
                    }
                    return {'warning': warning_mess}