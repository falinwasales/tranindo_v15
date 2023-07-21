from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import logging
import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_bom_kit = fields.Boolean(string="Is BoM Kit")

    no_po_do = fields.Char(string="Customer Reference", help="Reference from Sale.")
    do_ref = fields.Char(string="Customer Reference", help="Reference from Internal.", related="sale_id.client_order_ref")
    pos_po_do = fields.Char(string="Customer Reference", help="Reference from PoS.")

    # no_purchase_ref = fields.Char(string="Customer Reference")
    sticker_delivery = fields.Integer(string="No. of Box")
    is_print_kit = fields.Boolean(string="Is Print Kit Only")
    nama_dokumen = fields.Char(string="Nama Dokumen", 
    store=True
    )

    sj_binary = fields.Binary(string="Surat Jalan", attachment=True)
    sj_detail_product = fields.Boolean(string="Print detail Operation")

    diff_trans_del = fields.Boolean(string="Bool", compute="_get_value")
    contact_phone_show = fields.Boolean(string="Partner Phone")
    pos_account_move_id = fields.Many2one('account.move', string="PoS Move", related="pos_order_id.account_move")
    pos_picking_origin = fields.Char(string="Source Document")

    pos_created_bool = fields.Boolean(string="PoS Bool", compute="_get_pos_bool")
    sale_created_bool = fields.Boolean(string="Sale Bool", compute="_get_sale_bool")

    delivery_note = fields.Text(string="Notes")
    note = fields.Html('Notes', compute="_get_note_from_pos", store=True)
    stock_bom_id = fields.Many2one('stock.bom', string="Stock Bom")

    stock_bom_product_ids = fields.One2many('stock.bom', "picking_id", string="Invoice List")
    sale_order = fields.Many2one(
        'sale.order',
        string='Sale Order',
        compute='_compute_sale_order',
        store=True,
        readonly=True
    )

    @api.depends('origin')
    def _compute_sale_order(self):
        for picking in self:
            if picking.origin:
                sale_order = self.env['sale.order'].search([('name', '=', picking.origin)], limit=1)
                picking.sale_order = sale_order
            else:
                picking.sale_order = False
    # stock_picking_ids = fields.One2many('stock.picking', 'account_move_id', string='Stock Pickings')
    # @api.onchange('sj_binary')
    # def _onchange_sj_binary(self):
    #     if self.sj_binary:
    #         attachment_ids = self.sj_binary
    #         if isinstance(attachment_ids, int):
    #             attachment_ids = [attachment_ids]
            
    #         valid_attachment_ids = []
    #         invalid_attachment_ids = []

    #         for attachment_id in attachment_ids:
    #             attachment = self.env['ir.attachment'].browse(attachment_id)
    #             if attachment.exists():
    #                 valid_attachment_ids.append(attachment_id)
    #             else:
    #                 invalid_attachment_ids.append(attachment_id)

    #         if invalid_attachment_ids:
    #             # Handle invalid attachment IDs
    #             # For example, raise an error or log a warning

    #             attachments = self.env['ir.attachment'].search([('id', 'in', valid_attachment_ids)])
    #             self.nama_dokumen = ', '.join(attachments.mapped('name'))
    @api.depends('sj_binary')
    def _get_nama_dokumen(self):
        for record in self:
            if record.sj_binary:
                attachment = self.env['ir.attachment'].search([('res_model', '=', 'stock.picking'), ('res_id', '=', record.id)])
                if attachment:
                    record.nama_dokumen = attachment[0].name
                    
    def get_bom_kit(self):
        if self.state not in ('assigned', 'confirmed', 'draft', 'waiting'):
            result = []
            for line in self.move_ids_without_package:
                result.append((0, 0, {
                    'product_id': line.product_id.id,
                    'bom_qty': line.product_uom_qty,
                    'bom_product_qty': line.move_product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'picking_id': self.id
                    }))
            
            self.stock_bom_product_ids = result
        else:
            data = []
            for move in self.move_ids_without_package:
                data.append([move, move.product_move_bom, move.product_uom_qty, move.product_id])
                
            res = {}
            for table, bom_product, qty, prod in data:
                if bom_product in res:
                    res[bom_product]['cur'] = move.product_id.name
                    res[bom_product]['product'] = bom_product
                    res[bom_product]['table'] = table
                    if prod in res:
                        res[bom_product]['qty'] = qty
                else:
                    res[bom_product] = {'cur':move.product_id.name, 'product': bom_product, 'table':table, 'qty':qty,}
            
            data_new = []
            for line in res:
                data_new.append(res[line])

                    
            data_new2 = []
            for line2 in data_new:
                data_new2.append((0,0,{
                    'product_id': line2['product'].id,
                    'bom_qty': line2['qty'],
                    'bom_product_qty': line2['qty'],
                    'product_uom': line2['table'].product_uom.id,
                    'picking_id': self.id
                    }))
            
            # print('11111111111111111111111111')
            # print(data)
            # print('15151515151515151515151515')
            # print(res)
            # print('22222222222222222222222222')
            # print(data_new)
            # print('33333333333333333333333333')
            # print(data_new2)

            self.stock_bom_product_ids = data_new2
            self.update({
                'is_bom_kit' : True,
            })

    def action_cancel_option(self):
        view = self.env.ref('fal_tranindo_ext.stock_picking_cancel_opt')
        return {
            'name': ('Cancel Option'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.cancel.option',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {'picking_id': self.id},
        }

    def action_confirm(self):
        self.get_bom_kit()
        self._check_company()
        self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'draft' and not pl.move_ids)._generate_moves()
        # call `_action_confirm` on every draft move
        self.mapped('move_lines')\
            .filtered(lambda move: move.state == 'draft')\
            ._action_confirm()

        # run scheduler for moves forecasted to not have enough in stock
        self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))._trigger_scheduler()
        return True

        

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


        # YANG DARI PRODUCTIONNNNNNN 

    # def _get_product_bom_report(self):
    #     data = []
    #     for record in self.stock_bom_product_ids:
    #         data.append([record, record.product_id])
        
    #     res = {}
    #     for table, sale_product in data:
    #         if sale_product in res:
    #             res[sale_product]['product'] = sale_product
    #             res[sale_product]['table'] = table
    #         else:
    #             res[sale_product] = {'product': sale_product, 'table':table,}

    #     data_new = []
    #     for record in res:
    #         data_new.append(res[record])

    #     return data_new



        # YANG BENARRRRR DARI MAIN 


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

        ###################################### 
    
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

    @api.onchange('location_dest_id')
    def constraints_destination_location(self):
        for record in self:
            destination_location = record.location_dest_id

            if record.move_line_ids_without_package:
                for line in record.move_line_ids_without_package:
                    if destination_location != line.location_dest_id:
                        raise UserError(_("The Destination location cannot be different from Detailed Operations."))
                    
    @api.onchange('location_id')
    def constraints_destination_location(self):
        for record in self:
            destination_location = record.location_id

            if record.move_line_ids_without_package:
                for line in record.move_line_ids_without_package:
                    if destination_location != line.location_id:
                        raise UserError(_("The Frorm location cannot be different from Detailed Operations."))
