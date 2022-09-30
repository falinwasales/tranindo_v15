from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import logging
import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class TandaTerima(models.Model):
    _name = 'tanda.terima'
    _description = 'Tanda Terima'

    # def _get_name(self):
    #     return self.env['ir.sequence'].next_by_code('tanda.terima')

    name = fields.Char(string="Name", default="Draft")
    tanda_terima_date = fields.Date(string="Date")
    tt_invoice_id = fields.Many2one('account.move', string="Invoice")
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
        ], string="State", default="draft"
    )
    customer_id = fields.Many2one("res.partner", string="Customer")
    customer_street = fields.Char(string="Invoice Address")

    tt_account_ids = fields.One2many('account.move', "tt_nomor_id", string="Invoice List")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
        default=lambda self: self.env.company)

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, readonly=True)
    tt_total_subs = fields.Monetary(string="Total", default=lambda
                                self: self.env.user.company_id.currency_id.id, compute="_get_total_sub_tt")

    @api.depends("tt_account_ids")
    def _get_total_sub_tt(self):
        for record in self:
            record.tt_total_subs = 0
            if record.tt_account_ids:
                for invoice in record.tt_account_ids:
                    record.tt_total_subs += invoice.amount_residual

    @api.onchange('customer_id')
    def _get_customer_street(self):
        for record in self:
            record.customer_street = ""
            if record.customer_id:
                record.customer_street = record.customer_id.street

    @api.onchange('customer_id')
    def _get_customer_line(self):
        if self.tt_account_ids:
            self.write({"tt_account_ids": False})

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
            if self.name[:2] != "TT":
                sequence = self.env["ir.sequence"].next_by_code("tanda.terima")
                record.write({"name": sequence})

    def action_draft(self):
        for record in self:
            record.state = 'draft'