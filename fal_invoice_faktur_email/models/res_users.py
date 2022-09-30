from odoo import fields, models, api

class ResUser(models.Model):
    _inherit = 'res.users'

    customer_type_id = fields.Many2one('customer.type', string='Customer Type')