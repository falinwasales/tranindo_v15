from odoo import _, exceptions, fields, models, api
from datetime import date
from dateutil.relativedelta import relativedelta, MO, SU
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"
    
    def action_validate_invoice_payment(self):
        invoice_obj = self.env['account.move']
        # get context
        context = dict(self._context)
        active_ids = context.get('active_ids')
        for account in invoice_obj.browse(active_ids):
            for record in self:
                account.update({
                    'fal_paid_date': record.payment_date,
                    'fal_payment_method': record.journal_id.id,
                })

        if any(len(record.invoice_ids) != 1 for record in self):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        return self.post()

    def action_create_payments(self):
        payments = self._create_payments()

        account_move_obj = self.env['account.move']
        # get context
        active_ids = dict(self._context).get('active_ids')
        for account in account_move_obj.browse(active_ids):
            for record in self:
                account.update({
                    'fal_paid_date': record.payment_date,
                    'fal_payment_method': record.journal_id.id,
                })

        if self._context.get('dont_redirect_to_payments'):
            return True

        action = {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False},
        }
        if len(payments) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': payments.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', payments.ids)],
            })
        return action
