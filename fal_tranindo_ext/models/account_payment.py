from odoo import _, exceptions, fields, models, api
from datetime import date
from dateutil.relativedelta import relativedelta, MO, SU
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    fal_paid_date = fields.Date(string='Paid Date')
    fal_payment_method = fields.Many2one('account.journal', string='Payment Method')
    # name = fields.Char(string="Name")