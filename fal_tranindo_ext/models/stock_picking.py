from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import logging
import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    no_po_do = fields.Char(string="Customer Reference")

    do_ref = fields.Char(string="Customer Reference", related="sale_id.client_order_ref")
    # no_purchase_ref = fields.Char(string="Customer Reference")
    sticker_delivery = fields.Integer(string="No. of Box")
    is_print_kit = fields.Boolean(string="Is Print Kit Only")

    sj_binary = fields.Binary(string="SJ Binary")

    diff_trans_del = fields.Boolean(string="Bool", compute="_get_value")
    contact_phone_show = fields.Boolean(string="Partner Phone")

    def _get_value(self):
        for record in self:
            if record.sale_id:
                record.diff_trans_del = True
            else:
                record.diff_trans_del = False

    # @api.depends("sale_id")
    # def _get_customer_reference(self):
    #     for record in self:
    #         record.no_po_do = ""
    #         if record.sale_id.client_order_ref:
    #             record.no_po_do = record.sale_id.client_order_ref

    def _get_product_bom_report(self):
        data = []
        for record in self.move_ids_without_package:
            # for x in record.sale_line_id.product_id:
            data.append([record, record.sale_line_id.product_id, record.sale_line_id])
        
        res = {}
        for table, sale_product, sale_id in data:
            if sale_id in res:
                res[sale_id]['product'] = sale_id.product_id
                res[sale_id]['table'] = table
            else:
                res[sale_id] = {'product': sale_id.product_id, 'table':table,}

        data_new = []
        for record in res:
            data_new.append(res[record])

        return data_new
    
    def get_operation_detail(self):
        move_line_object = self.env['stock.move.line']
        for move in self.move_ids_without_package:
            uom = move.product_uom.id
            quant = 0
            if move.move_product_uom_qty > move.product_uom_qty or move.move_product_uom_qty == move.product_uom_qty:
                quant = move.product_uom_qty
            else:
                quant = move.move_product_uom_qty
            vals = {
                "product_id": move.product_id.id,
                "product_uom_id": uom,
                "location_id":self.location_id.id,
                "location_dest_id":self.location_dest_id.id,
                "move_id": move.id,
                "picking_id": self.id,
                "product_uom_qty": quant,
            }
            move_line_object.create(vals)
            # # for record in move.move_line_ids:
            #     # record.create(6, 0,[vals])
            # self.move_line_ids_without_package.update(vals)
            # print("******************")
            # print(move.id)

    
            