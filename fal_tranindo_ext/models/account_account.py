import time
from odoo import models, fields, api
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.tools.translate import _
from odoo.tools import append_content_to_html, DEFAULT_SERVER_DATE_FORMAT, html2plaintext
from odoo.exceptions import UserError

class AccountAccount(models.AbstractModel):
    _inherit = "account.account"

    @api.constrains('user_type_id')
    def _check_user_type_id_sales_purchase_journal(self):
        if not self:
            return

        self.flush(['user_type_id'])
        self._cr.execute('''
            SELECT account.id
            FROM account_account account
            JOIN account_account_type acc_type ON account.user_type_id = acc_type.id
            JOIN account_journal journal ON journal.default_account_id = account.id
            WHERE account.id IN %s
            AND acc_type.type IN ('receivable', 'payable')
            AND journal.type IN ('sale', 'purchase')
            LIMIT 1;
        ''', [tuple(self.ids)])

        # if self._cr.fetchone():
        #     raise ValidationError(_("The account is already in use in a 'sale' or 'purchase' journal. This means that the account's type couldn't be 'receivable' or 'payable'."))
