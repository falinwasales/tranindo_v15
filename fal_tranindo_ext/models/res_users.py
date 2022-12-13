from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class Resusers(models.Model):
    _inherit = 'res.users'

    pos_user = fields.Boolean(string="PoS Access")