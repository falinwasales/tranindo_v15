from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_type = fields.Selection(
        [
            ('email', 'Email'),
            ('email_via_collector', 'Email + diantar Fisik via Kolektor'),
            ('email_via_jne', 'Email + dikirim Fisik via JNE')
        ],
        string='Customer Type')