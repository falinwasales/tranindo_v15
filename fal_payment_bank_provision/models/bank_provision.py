from odoo import fields, models, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class BankProvision(models.Model):
    _name = 'fal.bank.provision'
    _inherit = ['mail.thread']
    _description = 'Bank Provision'

    x_studio_company = fields.Many2one('res.company', string="Company")
    name = fields.Char(string='No. Bank Provision')
    partner_id = fields.Many2one('res.partner', string="Customer")
    date_payment = fields.Date('Payment Date')
    amount = fields.Monetary(string='Amount')
    note = fields.Text("Note")
    state = fields.Selection([
        ('draft', 'Not Cashed'),
        ('reconcile', 'Cashed')
    ], default='draft', tracking=True)
    fal_bank_id = fields.Many2one(
        'res.bank', string="Issuing Bank")
    jurnal_dest_id = fields.Many2one(
        'account.journal',
        string="Cashed to", domain=[('type', '=', 'bank')])
    due_date = fields.Date(string="Due date")

    Notes = fields.Char('Notes', tracking=True)
    date_reconciled = fields.Date(
        string="Cashed Date", tracking=True)

    company_id = fields.Many2one(
        'res.company', 'Company')
    payment_id = fields.Many2one(
        'account.payment', 'Payment ID')
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=lambda self: self.jurnal_dest_id.currency_id)
    invoice_ids = fields.Many2many(
        'account.move', 'fal_bank_provision_invoice_rels',
        'bank_provision_id', 'move_id', string="Invoices", copy=False,
        readonly=True)
    communication = fields.Char(string='Memo')
    move_id = fields.Many2one('account.move', string="Journal Entry")
    # count_day = fields.Integer(
    #     string="Count Day", compute="_computeCountDate")
    count_day = fields.Integer(
        string="Count Day")

    pure_amount = fields.Monetary(string="Pure")
    keep_open = fields.Boolean(string="Keep Open")

    # def _get_total_signed(self):
    #     self.total_lines = 0
    #     for record in self.invoice_ids:
    #         self.total_lines += record.amount_total_signed


    def _computeCountDate(self):
        for data in self:
            datenow = fields.Date.context_today(self)
            dateliquidity = data.due_date
            if dateliquidity:
                d1 = fields.Date.from_string(dateliquidity)
                d2 = fields.Date.from_string(datenow)
                data.count_day = int((dateliquidity - datenow).days)

    @api.onchange('jurnal_dest_id')
    def _chg_jurnal_dest_id(self):
        self.currency_id = self.jurnal_dest_id.currency_id.id

    def cash(self):
        created_moves = self.env['account.move']
        line_list = []
        datenow = self.date_reconciled or fields.Date.context_today(self)
        for line in self:
            amount = 0
            name = "Provision - " + str(line.name)
            self_currency = line.currency_id.id
            # amount = line.amount
            db_acc = line.jurnal_dest_id.default_account_id.id
            cr_acc = line.payment_id.journal_id.default_account_id.id

            company_currency = line.payment_id.company_id.currency_id

            for record in line.invoice_ids:
                if record:
                    amount += record.amount_total_signed

            # Manage currency.
            if line.currency_id == company_currency:
                # Single-currency.
                self_currency = False
                amount_currency = 0.0
                amount = amount
            else:
                # Multi-currencies.
                amount_currency = amount
                amount = line.currency_id._convert(amount, company_currency, line.payment_id.company_id, datenow)

            if not line.keep_open:
                move_line_1 = {
                    'name': name,
                    'account_id': db_acc or False,
                    'debit': 0.0 if line.payment_id.partner_type == 'supplier' else amount,
                    'credit': amount if line.payment_id.partner_type == 'supplier' else 0.0,
                    'journal_id': line.jurnal_dest_id.id,
                    'currency_id': self_currency,
                    'amount_currency': -1 * amount_currency if line.payment_id.partner_type == 'supplier' else amount_currency,
                    'product_uom_id': 1,
                    'partner_id': self.partner_id.id,
                }
                line_list.append((0, 0, move_line_1))

                move_line_2 = {
                    'name': name,
                    'account_id': cr_acc or False,
                    'debit': amount if line.payment_id.partner_type == 'supplier' else 0.0,
                    'credit': 0.0 if line.payment_id.partner_type == 'supplier' else amount,
                    'journal_id': line.jurnal_dest_id.id,
                    'currency_id': self_currency,
                    'amount_currency': amount_currency if line.payment_id.partner_type == 'supplier' else -1 * amount_currency,
                    'product_uom_id': 1,
                    'partner_id': self.partner_id.id,
                }

                line_list.append((0, 0, move_line_2))
            else:
                move_line_1 = {
                    'name': name,
                    'account_id': db_acc or False,
                    'debit': line.pure_amount,
                    'credit': 0.0,
                    'journal_id': line.jurnal_dest_id.id,
                    'currency_id': self_currency,
                    'amount_currency': line.pure_amount,
                    'product_uom_id': 1,
                    'partner_id': self.partner_id.id,
                }
                line_list.append((0, 0, move_line_1))

                move_line_2 = {
                    'name': name,
                    'account_id': cr_acc or False,
                    'debit': 0.0,
                    'credit': line.pure_amount,
                    'journal_id': line.jurnal_dest_id.id,
                    'currency_id': self_currency,
                    'amount_currency': line.pure_amount,
                    'product_uom_id': 1,
                    'partner_id': self.partner_id.id,
                }
                line_list.append((0, 0, move_line_2))

        move_vals = {
            'ref': name,
            'date': datenow,
            'journal_id': self.jurnal_dest_id.id,
            'line_ids': line_list,
        }

        move = created_moves.create(move_vals)
        move.post()
        # Update State
        self.move_id = move.id
        self.state = 'reconcile'
        self.date_reconciled = datenow

    def uncash(self):
        self.move_id.button_cancel()
        self.state = 'draft'
