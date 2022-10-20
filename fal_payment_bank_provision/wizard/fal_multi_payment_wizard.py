# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    fal_bank_provision_id = fields.Char(string='No. Bank Provision')
    jurnal_dest_id = fields.Many2one(
        'account.journal',
        string="BANK Destination")
    due_date = fields.Date(string="Due date")
    is_provision = fields.Boolean(string="Is Provision?")

    @api.depends('payment_type',
                 'journal_id.inbound_payment_method_ids',
                 'journal_id.outbound_payment_method_ids')
    def _compute_payment_method_id(self):
        res = super(AccountPaymentRegister, self)._compute_payment_method_id()
        invoices = self._context.get('active_ids')
        invoice = self.env['account.move'].browse(invoices)[0]
        if self.journal_id:
            if invoice.is_inbound() == 'inbound':
                self.payment_method_id = self.env.ref(
                    'account.account_payment_method_manual_in').id
            else:
                self.payment_method_id = self.env.ref(
                    'account.account_payment_method_manual_out').id

        return res

    def _create_payment_vals_from_batch(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_batch(batch_result)
        res['fal_bank_provision_id'] = self.fal_bank_provision_id
        res['jurnal_dest_id'] = self.jurnal_dest_id.id
        res['due_date'] = self.due_date
        return res

    def _create_payments(self):
        res = super(AccountPaymentRegister, self)._create_payments()
        inv_list = []
        for payment in res:
            if payment.reconciled_invoice_ids:
                inv_list.append((6, 0, payment.reconciled_invoice_ids.ids))
            else:
                inv_list = False
            prov = []
            provision_in = self.env.ref(
                'fal_payment_bank_provision.account_payment_method_bankprov_in')
            prov.append(provision_in.id)
            provision_out = self.env.ref(
                'fal_payment_bank_provision.account_payment_method_bankprov_out')
            prov.append(provision_out.id)

            for line in self.payment_wizard_line_ids:
                if payment.payment_method_id.id in prov:
                    data = {
                        'name': line.fal_bank_provision_id,
                        'state': 'draft',
                        'partner_id': payment.partner_id.id,
                        'payment_id': payment.id,
                        'date_payment': payment.date,
                        'amount': payment.amount,
                        'invoice_ids': inv_list,
                        'note': payment.ref,
                        'due_date': self.due_date,
                        'jurnal_dest_id': self.jurnal_dest_id.id,
                        'currency_id': payment.currency_id.id
                    }
                    self.env['fal.bank.provision'].create(data)

        if self.fal_split_multi_payment:
            for line in self.payment_wizard_line_ids:
                if line.is_provision:
                    if not line.fal_bank_provision_id:
                        raise UserError('Please set No. Bank Provision')
        return res

    @api.onchange('payment_method_line_id')
    def _onchange_payment_method_line_id(self):
        if self.payment_method_line_id:
            prov = []
            provision_in = self.env.ref(
                'fal_payment_bank_provision.account_payment_method_bankprov_in')
            prov.append(provision_in.id)
            provision_out = self.env.ref(
                'fal_payment_bank_provision.account_payment_method_bankprov_out')
            prov.append(provision_out.id)
            if self.payment_method_line_id.payment_method_id.id in prov:
                self.is_provision = True
            else:
                self.is_provision = False

    @api.onchange('fal_bank_provision_id')
    def _onchange_fal_bank_provision_id(self):
        if self.payment_date:
            for wizard_line in self.payment_wizard_line_ids:
                wizard_line.fal_bank_provision_id = self.fal_bank_provision_id


class fal_multi_payment_wizard(models.TransientModel):
    _inherit = "fal.multi.payment.wizard"

    fal_bank_provision_id = fields.Char(string='No. Bank Provision')
    is_provision = fields.Boolean(
        string="Is Provision?", related="register_payments_id.is_provision")

    def _prepare_payment_vals(self, invoices):
        res = super(fal_multi_payment_wizard, self)._prepare_payment_vals(invoices)
        res.update({
            'payment_method_line_id': self.payment_method_line_id.id,
            'fal_bank_provision_id': self.fal_bank_provision_id,
            'jurnal_dest_id': self.register_payments_id.jurnal_dest_id.id,
            'due_date': self.register_payments_id.due_date
        })
        return res
