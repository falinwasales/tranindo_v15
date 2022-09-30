from odoo import models, fields, api
# import base64
# import csv
# import math
# import logging
# import datetime
# from datetime import date
# from datetime import datetime

# _logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    # partner_npwp = fields.Char(string='NPWP', size=15)
    partner_pkp_status = fields.Selection(
        [
            ('pkp', 'PKP'),
            ('nonpkp', 'Non PKP')
        ], string='Status PKP'
    )
    partner_ppkp = fields.Char(string='PPKP')
