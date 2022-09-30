from odoo import fields, models, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    name = fields.Char(readonly=True, copy=False, string="Payment Name")
    fal_bank_provision_id = fields.Char(string='No. Bank Provision')
    jurnal_dest_id = fields.Many2one(
        'account.journal',
        string="BANK Destination")
    due_date = fields.Date(string="Due date")
    is_provision = fields.Boolean(string="Is Provision?")


class AccountJournal(models.Model):
    _inherit = "account.journal"

    fal_is_provision = fields.Boolean(
        string='Enable Bank Provision', default=False,
        help="Check this box if this to enable Bank Provision."
    )


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['provin'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
        res['provout'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
        return res
