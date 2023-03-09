from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)


class product_product(models.Model):
    _inherit = 'product.template'

    purchase_product = fields.Many2one('purchase.order.line', string="Purchase Product Order Line")

    product_po_line_field = fields.Many2many('purchase.order.line', 'purchase_product', string='Purchase Order Line')

    def _get_current_compnay(self):
        return self.env.company

    company_id = fields.Many2one(
        'res.company', 'Company', index=1, default=_get_current_compnay)

    @api.constrains('name')
    def _check_name(self):
        if self.name:
            product_rec = self.env['product.template'].search(
                [('name', '=', self.name)])
            if len(product_rec) > 1:
                raise ValidationError(_('Theres already product with the same name!!!'))


