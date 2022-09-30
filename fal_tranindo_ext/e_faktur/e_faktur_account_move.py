from odoo import models, fields, api
import base64
import csv
import math
import logging
import datetime
from datetime import date
from datetime import datetime

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    account_npwp = fields.Char(string='NPWP', size=15)
    account_ppkp = fields.Char(string='PPKP')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        if self.partner_id:
            self.account_npwp = self.partner_id.vat
            if self.partner_id.partner_pkp_status == 'pkp':
                self.account_ppkp = self.partner_id.partner_ppkp
        return res