from odoo import fields, models, api, _
from odoo.exceptions import UserError
import math
import logging

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    disc_round = fields.Float(string="Disc Round", compute="_round_discount")
    product_qty_available = fields.Float(string="Qty Available", related="product_id.qty_available")

    @api.depends('discount')
    def _round_discount(self):
        for record in self:
            if int(repr(record.discount)[-1]) == 5:
                record.disc_round = math.ceil(record.discount * 100)/100
            else:
                record.disc_round = round(record.discount,2)