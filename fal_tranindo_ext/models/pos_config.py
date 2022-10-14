from odoo import fields, models, api
from odoo import _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = "pos.config"

    image_pos = fields.Binary(string="Picture")
    report_text = fields.Text(string="Additional Info")
    pos_internal = fields.Boolean(string="PoS Internal")

    default_warehouse_location = fields.Many2one("stock.location",string="Default PIcking")
    default_location_dest = fields.Many2one("stock.location",string="Default Destination")

    default_sequence_id = fields.Many2one("ir.sequence", string="Default Sequence")