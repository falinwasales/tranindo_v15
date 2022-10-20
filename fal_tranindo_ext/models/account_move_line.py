import time
import math
from odoo import models, fields, api
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.tools.translate import _
from odoo.tools import append_content_to_html, DEFAULT_SERVER_DATE_FORMAT, html2plaintext
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    follow_block = fields.Boolean(string="Booean Field", default=False)
    
    blocked = fields.Boolean(string='No Follow-up', readonly=False,
        help="You can check this box to mark this journal item as a litigation with the associated partner")

    disc_round = fields.Float(string="Disc Round", compute="_round_discount")

    _sql_constraints = [
        (
            'check_credit_debit',
            'CHECK(credit + debit>=0 AND credit * debit=0)',
            'Wrong credit or debit value in accounting entry !'
        ),
        # (
        #     'check_accountable_required_fields',
        #      "CHECK(COALESCE(display_type IN ('line_section', 'line_note'), 'f') OR account_id IS NOT NULL)",
        #      "Missing required account on accountable invoice line."
        # ),
        (
            'check_non_accountable_fields_null',
             "CHECK(display_type NOT IN ('line_section', 'line_note') OR (amount_currency = 0 AND debit = 0 AND credit = 0 AND account_id IS NULL))",
             "Forbidden unit price, account and quantity on non-accountable invoice line"
        ),
        (
            'check_amount_currency_balance_sign',
            '''CHECK(
                (
                    (currency_id != company_currency_id)
                    AND
                    (
                        (debit - credit <= 0 AND amount_currency <= 0)
                        OR
                        (debit - credit >= 0 AND amount_currency >= 0)
                    )
                )
                OR
                (
                    currency_id = company_currency_id
                    AND
                    ROUND(debit - credit - amount_currency, 2) = 0
                )
            )''',
            "The amount expressed in the secondary currency must be positive when account is debited and negative when "
            "account is credited. If the currency is the same as the one from the company, this amount must strictly "
            "be equal to the balance."
        ),
    ]

    @api.depends('discount')
    def _round_discount(self):
        for record in self:
            if int(repr(record.discount)[-1]) == 5:
                record.disc_round = math.ceil(record.discount * 100)/100
            else:
                record.disc_round = round(record.discount,2)

    @api.onchange(fields.Date.today())
    def _get_value(self):
        for record in self:
            today = fields.Date.today()
            if today > record.date_maturity:
                record.blocked = True
            else:
                record.blocked = False