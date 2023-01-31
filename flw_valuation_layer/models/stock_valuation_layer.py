from odoo import _, exceptions, fields, models, api
import datetime
from dateutil.relativedelta import relativedelta, MO, SU
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from odoo.tools import float_round, date_utils
import math
import json

class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    x_invoiced_layer = fields.Boolean(string="Invoiced", store="True")

    @api.depends('stock_move_id')
    def get_bool_result(self):
        for record in self:
            record.x_invoiced_layer = False
            if record.stock_move_id.account_move_ids:
                record.x_invoiced_layer = True

    def turn_invoiced_bool(self):
        for record in self:
            record.x_invoiced_layer = False
            if record.stock_move_id.account_move_ids:
                record.x_invoiced_layer = True

    # x_account_move_ids = fields.

    