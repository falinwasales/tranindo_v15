from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    salesperson = fields.Many2one('res.users', string="Salesperson")
    pos_comission = fields.Float(string="Comission")
    partner_comission = fields.Many2one("res.partner", string="Partner Comission")
    subtotal_tax = fields.Float(string="Subtotal W/O Tax", compute="subtotal_get")

    vendor_bill_id = fields.Many2one("account.move", string="Vendor Bill ID",compute="get_vendor_bill")

    vendor_bill_ids = fields.Many2many("account.move", string="Vendor Bill ID",compute="get_vendor_bill_ids")
    

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