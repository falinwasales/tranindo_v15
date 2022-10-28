from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import logging
import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    note = fields.Char(string="Note")

    # @api.model
    # def create(self, vals):
    #     """ Override to handle the "inventory mode" and create a quant as
    #     superuser the conditions are met.
    #     """
    #     if self._is_inventory_mode() and any(f in vals for f in ['inventory_quantity', 'inventory_quantity_auto_apply']):
    #         allowed_fields = self._get_inventory_fields_create()
    #         print('8888888888888')
    #         print(allowed_fields)
    #         if any(field for field in vals.keys() if field not in allowed_fields):
    #             print('999999999999999999999')
    #             print(vals.keys())
    #             raise UserError(_("Quant's creation is restricted, you can't do this operation."))

    #         inventory_quantity = vals.pop('inventory_quantity', False) or vals.pop(
    #             'inventory_quantity_auto_apply', False) or 0
    #         # Create an empty quant or write on a similar one.
    #         product = self.env['product.product'].browse(vals['product_id'])
    #         location = self.env['stock.location'].browse(vals['location_id'])
    #         lot_id = self.env['stock.production.lot'].browse(vals.get('lot_id'))
    #         package_id = self.env['stock.quant.package'].browse(vals.get('package_id'))
    #         owner_id = self.env['res.partner'].browse(vals.get('owner_id'))
    #         quant = self._gather(product, location, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True)
    #         if lot_id:
    #             quant = quant.filtered(lambda q: q.lot_id)

    #         if quant:
    #             quant = quant[0].sudo()
    #         else:
    #             quant = self.sudo().create(vals)
    #         # Set the `inventory_quantity` field to create the necessary move.
    #         quant.inventory_quantity = inventory_quantity
    #         quant.user_id = vals.get('user_id', self.env.user.id)
    #         quant.inventory_date = fields.Date.today()

    #         return quant
    #     res = super(StockQuant, self).create(vals)
    #     if self._is_inventory_mode():
    #         res._check_company()
    #     return res

    # @api.model
    # def _get_inventory_fields_create(self):
    #     """ Returns a list of fields user can edit when he want to create a quant in `inventory_mode`.
    #     """
    #     return ['product_id', 'location_id', 'lot_id', 'package_id', 'owner_id', 'note'] + self._get_inventory_fields_write()

    # @api.model
    # def _get_inventory_fields_write(self):
    #     """ Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`.
    #     """
    #     fields = ['inventory_quantity', 'inventory_quantity_auto_apply', 'inventory_diff_quantity',
    #               'inventory_date', 'user_id', 'inventory_quantity_set', 'is_outdated', 'note']
    #     return fields