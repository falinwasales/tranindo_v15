from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    product_cost = fields.Float(string="Product Cost", store=True)
    # count_purchase = fields.Float(string="Count Purchase", store=True, compute="_count_purchase")

    # @api.