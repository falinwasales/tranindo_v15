import base64
from odoo import fields, models, api

class CustomerType(models.Model):
    _name = 'customer.type'
    _description = 'Customer type of a customer'

    user_ids = fields.Many2one('res.users', string='Reminder Person')
    customer_type = fields.Selection(
        [
            ('email', 'Email'),
            ('email_via_collector', 'Email + diantar Fisik via Kolektor'),
            ('email_via_jne', 'Email + dikirim Fisik via JNE')
        ],
        string='Customer Type')

