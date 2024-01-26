from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
import pytz

import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    salesperson = fields.Many2one('res.users', string="Salesperson")
    pos_comission = fields.Float(string="Comission")
    partner_comission = fields.Many2one("res.partner", string="Partner Comission")
    subtotal_tax = fields.Float(string="Subtotal W/O Tax", compute="subtotal_get")

    vendor_bill_id = fields.Many2one("account.move", string="Vendor Bill ID",compute="get_vendor_bill")

    vendor_bill_ids = fields.Many2many("account.move", string="Vendor Bill IDs",compute="get_vendor_bill_ids")

    invoice_status = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancel')
        ], string='Invoice Status', readonly=True, related="account_move.state")

    invoice_payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy')
    ], string='Payment Status', readonly=True, related="account_move.payment_state")



    def get_vendor_bill(self):
        for record in self:
            record.vendor_bill_id = False
            vendor =  self.env['account.move'].search([("pos_comission_id","=",record.id),('move_type','in',['in_invoice'])],limit=1)
            if vendor:
                record.vendor_bill_id = vendor[-1].id

    def get_vendor_bill_ids(self):
        for record in self:
            record.vendor_bill_ids = False
            vendor =  self.env['account.move'].search([("pos_comission_id","=",record.id),('move_type','in',['in_invoice'])])
            if vendor:
                record.vendor_bill_ids = vendor

    vendor_count_field = fields.Integer(compute='_compute_invoice_count', string='Vendor Bill Order Count')

    def _compute_invoice_count(self):
        self.vendor_count_field = len(self.vendor_bill_ids)


    @api.depends("lines")
    def subtotal_get(self):
        for record in self:
            record.subtotal_tax = 0
            for lines in record.lines:
                if lines:
                    record.subtotal_tax += lines.price_subtotal

    def _prepare_invoice_vals(self):
        vals = super()._prepare_invoice_vals()
        if self.company_id.country_id.code == 'ID':
            vals.update({'l10n_id_kode_transaksi': self.partner_id.l10n_id_kode_transaksi})
        return vals

    def action_view_vendor_bill(self):
        self.ensure_one()
        invoice_order_ids = self.vendor_bill_ids.ids
        action = {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
        }
        action.update({
            'name': _("Vendor Bill"),
            'domain': [('id', 'in', invoice_order_ids)],
            'view_mode': 'tree,form,kanban',
            'context': {
                'default_move_type': 'in_invoice',
                "create":False
            }
        })
        return action

    def create_vendor_bill_pos(self):
            # tax = 3
            # if record.partner_id.vat:
            #     tax = 2.5
            default_seq_vendor = self.config_id
            create_seq = self.env["ir.sequence"].next_by_code(default_seq_vendor.default_sequence_vendor.code)
            create = self.env['account.move'].create({
                "name": create_seq,
                "partner_id": self.partner_comission.id,
                "invoice_line_ids": [(0,0,{"product_id":3695, "name":"komisi","price_unit": self.subtotal_tax*(self.pos_comission/100), "quantity":1,"product_uom_id":1}),(0,0,{"product_id":4251, "name":"Pajak","price_unit": -((self.subtotal_tax*(self.pos_comission/100))*0.03), "quantity":1,"product_uom_id":1})],
                "move_type": "in_invoice",
                "pos_comission_id": self.id,
            })
            return create

    def _create_order_picking(self):
        self.ensure_one()
        if self.to_ship:
            self.lines._launch_stock_rule_from_pos_order_lines()
        else:
            if self._should_create_picking_real_time():
                picking_type = self.config_id.picking_type_id
                if self.partner_id.property_stock_customer:
                    destination_id = self.partner_id.property_stock_customer.id
                elif not picking_type or not picking_type.default_location_dest_id:
                    destination_id = self.env['stock.warehouse']._get_partner_locations()[0].id
                else:
                    destination_id = picking_type.default_location_dest_id.id

                account_move_name = self.account_move if self.account_move else ''

                name_name = '%s' % (self.name) if not account_move_name else '%s (%s)' % (self.name, account_move_name.name)

                pickings = self.env['stock.picking']._create_picking_from_pos_order_lines(destination_id, self.lines, picking_type, self.partner_id)
                pickings.write({'pos_session_id': self.session_id.id, 'pos_order_id': self.id, 'pos_picking_origin': name_name, 'pos_po_do':name_name, 
                'origin': name_name, 'pos_account_move_id': account_move_name})

                # if self.config_id.pos_internal:
                #     picking = self.config_id.default_warehouse_location
                #     location = self.config_id.default_location_dest
                #     sequence_code = self.config_id.default_sequence_id.code

                #     sequence = self.env["ir.sequence"].next_by_code(sequence_code)

                #     tranindo_brenn = pickings.copy({'name':sequence, 'picking_type_id':self.picking_type_id.id,'location_id':picking.id, 
                #         'location_dest_id': location.id, 'origin':pickings.pos_picking_origin, 'no_po_do':pickings.pos_picking_origin})
                #     tranindo_brenn.move_ids_without_package.write({'location_id':location.id,'location_dest_id': pickings.location_id.id})


