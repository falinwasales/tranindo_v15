from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    do_container = fields.Char(string="DO Number", compute="_get_picking_ids_refereces")
    invoice_container = fields.Char(string="Invoice Number", compute="_get_invoice_ids_refereces")
    sale_boolean = fields.Boolean(string="Sales Boolean", compute="_get_bool_value")
    market = fields.Char(string="market", related="partner_id.partner_market")
    wilayah = fields.Char(string="Wilayah", related="partner_id.partner_wilayah")
    is_final_customer = fields.Boolean(string="Is final")
    final_customer = fields.Many2one("res.partner", string="Final Customer")

    invoice_street = fields.Many2one("res.partner", string="Invoice Address")
    delivery_street = fields.Many2one("res.partner", string="Delivery Address")

    @api.onchange('final_customer')
    def _onchange_delivery_invoice(self):
        for record in self:
            if record.final_customer:
                record.invoice_street = record.final_customer
                record.delivery_street = record.final_customer

    @api.depends('state')
    def _get_bool_value(self):
        for record in self:
            if record.state == "done" or record.state == "sale":
                record.sale_boolean = True
            else:
                record.sale_boolean = False

    @api.depends("picking_ids")
    def _get_picking_ids_refereces(self):
        for record in self:
            data = []
            name = ""
            for ids in record.picking_ids.filtered(lambda x: x.state == "done"):
                data.append(ids.name)
                if len(ids) > 1:
                    name = "%s," % (data)
                else:
                    name = "%s" % (data)
            record.do_container = name[1:-1].replace("'", "")

    @api.depends("invoice_ids")
    def _get_invoice_ids_refereces(self):
        for record in self:
            data = []
            name = ""
            for ids in record.invoice_ids.filtered(lambda x: x.state == "posted"):
                data.append(ids.name)
                if len(ids) > 1:
                    name = "%s," % (data)
                else:
                    name = "%s" % (data)
            record.invoice_container = name

    @api.depends('picking_ids')
    def _fal_get_stock_picking(self):
        for sale_order in self:
            sale_order.fal_stock_picking_id = sale_order.picking_ids[0].id if sale_order.picking_ids else False

    fal_stock_picking_id = fields.Many2one("stock.picking", compute='_fal_get_stock_picking', string="Delivery")

    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #     for rec in self:
    #         rec.picking_ids.write({"diff_trans_del": True})
    #     return res

    @api.constrains('order_line')
    def _constraints_qty_on_hand(self):
        for record in self.order_line:
            if record.product_qty_available< 1:
                raise ValidationError(_('The product lack of quantity on hand'))

    @api.model
    def create(self, vals):
        if vals.get('client_order_ref') and vals.get('company_id'):
            self._check_duplicate_customer_reference(vals['client_order_ref'], vals['company_id'])
        res = super(SaleOrder, self).create(vals)
        return res

    def write(self, values):
        if values.get('client_order_ref'):
            self._check_duplicate_customer_reference(values.get('client_order_ref'), self.company_id.id)
        res = super(SaleOrder, self).write(values)
        return res
        
    def _check_duplicate_customer_reference(self, cust_ref, company):
        if self.search([('client_order_ref', '=', cust_ref), ('company_id', '=', company)]):
            raise UserError(_("Duplicated Customer Reference detected. You probably encoded twice the same Quotation."))
