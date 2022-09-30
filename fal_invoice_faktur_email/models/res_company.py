from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    account_number = fields.Char(string='Account Number')
    branch = fields.Char(string='Branch')