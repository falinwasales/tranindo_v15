from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, html_keep_url, is_html_empty
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    do_container = fields.Char(string="DO Number", compute="_get_picking_ids_refereces")
    invoice_container = fields.Char(string="Invoice Number", compute="_get_invoice_ids_refereces", store=True)
    sale_boolean = fields.Boolean(string="Sales Boolean", compute="_get_bool_value")
    market = fields.Char(string="market", related="partner_id.partner_market")
    wilayah = fields.Char(string="Wilayah", related="partner_id.partner_wilayah")
    is_final_customer = fields.Boolean(string="Is final")
    final_customer = fields.Many2one("res.partner", string="Final Customer")

    invoice_street = fields.Many2one("res.partner", string="Invoice Address")
    delivery_street = fields.Many2one("res.partner", string="Delivery Address")

    user_id = fields.Many2one(
        'res.users', string='Salesperson', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ),)

    #FITUR COMMISSION SO
    so_commission = fields.Float(string="Commission")
    partner_commission = fields.Many2one("res.partner", string="Partner Commission")
    subtotal_tax = fields.Float(string="Subtotal W/O Tax", compute="subtotal_get")
    vendor_bill_ids = fields.Many2many("account.move", string="Vendor Bill IDs",compute="get_vendor_bill_ids")
    vendor_count_field = fields.Integer(compute='_compute_invoice_count', string='Vendor Bill Order Count')

    def get_vendor_bill_ids(self):
        for record in self:
            record.vendor_bill_ids = False
            vendor =  self.env['account.move'].search([("so_id","=",record.id),('move_type','in',['in_invoice'])])
            if vendor:
                record.vendor_bill_ids = vendor

    def _compute_invoice_count(self):
        self.vendor_count_field = len(self.vendor_bill_ids)

    @api.depends("order_line")
    def subtotal_get(self):
        for record in self:
            record.subtotal_tax = 0
            for lines in record.order_line:
                if lines:
                    record.subtotal_tax += lines.price_subtotal

    def create_vendor_bill_pos(self):
            create_seq = self.env["ir.sequence"].next_by_code('bill.commission') or '/'
            create = self.env['account.move'].create({
                "name": create_seq,
                "partner_id": self.partner_commission.id,
                "invoice_line_ids": [(0,0,{"product_id":3695, "name":"komisi","price_unit": self.subtotal_tax*(self.so_commission/100), "quantity":1,"product_uom_id":1}),(0,0,{"product_id":4251, "name":"Pajak","price_unit": -((self.subtotal_tax*(self.so_commission/100))*0.03), "quantity":1,"product_uom_id":1})],
                "move_type": "in_invoice",
                "so_id": self.id,
            })
            return create
    
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
            for ids in record.picking_ids.filtered(lambda x: not x.state == "cancel"):
                data.append(ids.name)
                if len(ids) > 1:
                    name = "%s," % (data)
                else:
                    name = "%s" % (data)
            record.do_container = name[1:-1].replace("'", "")

    @api.depends("invoice_ids.name")
    def _get_invoice_ids_refereces(self):
        for record in self:
            if record.invoice_ids:
                record.invoice_container = record.invoice_ids[0].name if record.invoice_ids[0].state == 'posted' else False

    @api.depends('picking_ids')
    def _fal_get_stock_picking(self):
        for sale_order in self:
            sale_order.fal_stock_picking_id = sale_order.picking_ids[0].id if sale_order.picking_ids else False

    fal_stock_picking_id = fields.Many2one("stock.picking", compute='_fal_get_stock_picking', string="Delivery")

    @api.depends('picking_ids')
    def _fal_get_stock_pickings(self):
        for sale_order in self:
            sale_order.fal_stock_picking_ids = sale_order.picking_ids.ids or False

    fal_stock_picking_ids = fields.Many2many("stock.picking", compute='_fal_get_stock_pickings', string="Deliveries")

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

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        - Sales Team
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)

        addr = self.partner_id.address_get(['delivery', 'invoice'])
        # partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
        }
        # user_id = partner_user.id
        # if not self.env.context.get('not_self_saleperson'):
        #     user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
        # if user_id and self.user_id.id != user_id:
        #     values['user_id'] = user_id

        if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms'):
            if self.terms_type == 'html' and self.env.company.invoice_terms_html:
                baseurl = html_keep_url(self.get_base_url() + '/terms')
                values['note'] = _('Terms & Conditions: %s', baseurl)
            elif not is_html_empty(self.env.company.invoice_terms):
                values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
        if not self.env.context.get('not_self_saleperson') or not self.team_id:
            default_team = self.env.context.get('default_team_id', False) or self.partner_id.team_id.id
            values['team_id'] = self.env['crm.team'].with_context(
                default_team_id=default_team
            )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)])
        self.update(values)

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).', self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'user_id': self.user_id.id,
            'invoice_user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(self.partner_invoice_id.id)).id,
            'partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'payment_reference': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'category_first_line': self.order_line[0].product_id.categ_id.id
        }
        return invoice_vals