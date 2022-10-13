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
    pos_account_move_id = fields.Many2one('account.move', string="PoS Move", related="pos_order_id.account_move")
    pos_picking_origin = fields.Char(string="Source Document", compute="_get_origin")
    pos_po_do = fields.Char(string="Customer Reference", related="pos_picking_origin")

    def _get_origin(self):
        for record in self:
            record.pos_picking_origin = ""
            if record.pos_account_move_id:
                record.pos_picking_origin = '%s (%s)' % (record.pos_order_id.name, record.pos_account_move_id.name)

    def _get_value(self):
        for record in self:
            if record.sale_id:
                record.diff_trans_del = True
            else:
                record.diff_trans_del = False

    def _get_product_bom_report(self):
        data = []
        for record in self.move_ids_without_package:
            # for x in record.sale_line_id.product_id:
            data.append([record, record.product_id, record.product_move_bom])
        
        res = {}
        for table, sale_product, bom in data:
            if bom in res:
                res[bom]['product'] = bom
                res[bom]['table'] = table
            else:
                res[bom] = {'product': bom, 'table':table,}

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
