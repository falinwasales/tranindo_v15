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