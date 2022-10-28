from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import logging
import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    no_po_do = fields.Char(string="Customer Reference", help="Reference from Sale.")
    do_ref = fields.Char(string="Customer Reference", help="Reference from Internal.", related="sale_id.client_order_ref")
    pos_po_do = fields.Char(string="Customer Reference", help="Reference from PoS.")

    # no_purchase_ref = fields.Char(string="Customer Reference")
    sticker_delivery = fields.Integer(string="No. of Box")
    is_print_kit = fields.Boolean(string="Is Print Kit Only")

    sj_binary = fields.Binary(string="SJ Binary")
    sj_detail_product = fields.Boolean(string="Print detail Operation")

    diff_trans_del = fields.Boolean(string="Bool", compute="_get_value")
    contact_phone_show = fields.Boolean(string="Partner Phone")
    pos_account_move_id = fields.Many2one('account.move', string="PoS Move", related="pos_order_id.account_move")
    pos_picking_origin = fields.Char(string="Source Document")

    pos_created_bool = fields.Boolean(string="PoS Bool", compute="_get_pos_bool")
    sale_created_bool = fields.Boolean(string="Sale Bool", compute="_get_sale_bool")

    delivery_note = fields.Text(string="Notes")
    note = fields.Html('Notes', compute="_get_note_from_pos", store=True)

    # @api.model
    # def _create_picking_from_pos_order_lines(self, location_dest_id, lines, picking_type, partner=False):
    #     _logger.warning('_____________________________________')
    #     _logger.warning('__________________BIKIN PICKING___________________')
    #     """We'll create some picking based on order_lines"""

    #     pickings = self.env['stock.picking']
    #     stockable_lines = lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty, precision_rounding=l.product_id.uom_id.rounding))
    #     if not stockable_lines:
    #         return pickings
    #     positive_lines = stockable_lines.filtered(lambda l: l.qty > 0)
    #     negative_lines = stockable_lines - positive_lines

    #     if positive_lines:
    #         location_id = picking_type.default_location_src_id.id
    #         positive_picking = self.env['stock.picking'].create(
    #             self._prepare_picking_vals(partner, picking_type, location_id, location_dest_id)
    #         )

    #         _logger.warning('_____________________________________')
    #         _logger.warning('__________________Check positive PICKING___________________')
    #         _logger.warning(positive_picking)
    #         _logger.warning(positive_picking.state)
    #         positive_picking._create_move_from_pos_order_lines(positive_lines)
    #         #             try:
    #         # #                 with self.env.cr.savepoint():
    #         # #                     positive_picking._action_done()
    #         #             except (UserError, ValidationError):
    #         #                 pass

    #         pickings |= positive_picking
    #     if negative_lines:
    #         if picking_type.return_picking_type_id:
    #             return_picking_type = picking_type.return_picking_type_id
    #             return_location_id = return_picking_type.default_location_dest_id.id
    #         else:
    #             return_picking_type = picking_type
    #             return_location_id = picking_type.default_location_src_id.id

    #         negative_picking = self.env['stock.picking'].create(
    #             self._prepare_picking_vals(partner, return_picking_type, location_dest_id, return_location_id)
    #         )
    #         negative_picking._create_move_from_pos_order_lines(negative_lines)
    #         #             try:
    #         #                 with self.env.cr.savepoint():
    #         # #                     negative_picking._action_done()
    #         #             except (UserError, ValidationError):
    #         #                 pass
    #         pickings |= negative_picking
    #     _logger.warning('_____________________________________')
    #     _logger.warning('__________________Check positive PICKING___________________')
    #     _logger.warning(pickings)
    #     for pick_cuk in pickings:
    #         _logger.warning(pick_cuk.state)
    #         #         _logger.warning(BABILAGI)
    #     return pickings
    

    @api.depends('pos_order_id.note')
    def _get_note_from_pos(self):
        for record in self:
            if record.pos_order_id:
                record.note = record.pos_order_id.note

    def _get_sale_bool(self):
        for record in self:
            record.sale_created_bool = False
            if record.sale_id:
                record.sale_created_bool = True

    def _get_pos_bool(self):
        for record in self:
            record.pos_created_bool = False
            if record.pos_order_id:
                record.pos_created_bool = True

    def _get_value(self):
        for record in self:
            if record.sale_id:
                record.diff_trans_del = True
            else:
                record.diff_trans_del = False

    def _get_product_bom_report(self):
        data = []
        for record in self.move_ids_without_package:
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
