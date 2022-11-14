from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import logging
import odoo.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)

class StockCancelOption(models.TransientModel):
    _name = 'stock.cancel.option'

    picking_id = fields.Many2one('stock.picking', string="Picking")

    def action_cancelled(self):
        search_transfer = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        search_transfer.mapped('move_lines')._action_cancel()
        search_transfer.write({'is_locked': True})
        return True