# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_register_payment(self):
        res = super(AccountMove, self).action_register_payment()
        context = res.get('context')
        # not stable, default multi payment is False
        # if len(context.get('active_ids')) > 1 and context.get('active_model') == 'account.move':
        #     context.update({'default_fal_split_multi_payment': True})
        context.update({'default_is_invoice': True})
        return res
