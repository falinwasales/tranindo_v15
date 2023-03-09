from odoo import _, exceptions, fields, models, api
import datetime
from dateutil.relativedelta import relativedelta, MO, SU
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
from odoo.tools import float_round, date_utils
import math
import json

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_date = fields.Date(string="Sale Date")