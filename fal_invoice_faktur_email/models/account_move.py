import base64
# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.tools.misc import formatLang, get_lang
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from num2words import num2words
from ast import literal_eval
from odoo.tools.mimetypes import guess_mimetype
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp


class AccountMove(models.Model):
    _inherit = 'account.move'

    faktur_file = fields.Binary(string='Faktur Pajak', attachment=True)
    po_file = fields.Binary(string='Purchase Order', attachment=True)
    invoice_file = fields.Binary(string='Invoice', attachment=True)
    surat_jalan_file_upload = fields.Binary(string='Surat Jalan', attachment=True)

    faktur_file_name = fields.Char(string='Faktur Pajak Name')
    po_file_name = fields.Char(string='Purchase Order Name')
    invoice_file_name = fields.Char(string='Invoice Name')
    surat_jalan_file_upload_name = fields.Char(string='Surat Jalan Name')

    customer_reference = fields.Char(string='Customer Reference', compute='_get_customer_reference')

    invoice_payment_state = fields.Char(string="Payment State")

    
    agreement_file = fields.Many2many(
        'ir.attachment',
        'class_ir_attachments_rel',
        'class_id',
        'attachment_id',
        string="Agreement files",
        required=False)


    @api.depends('invoice_line_ids')
    def _get_customer_reference(self):
        for record in self:
            # record.customer_reference = ''
            record.customer_reference = ''
            if record.invoice_line_ids:
                for line in record.invoice_line_ids:
                    if line.sale_line_ids:
                        for test in line.sale_line_ids:
                            if test.order_id:
                                for result in test.order_id:
                                    if result.client_order_ref:
                                        record.customer_reference = result.client_order_ref
                            
    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref(self._get_mail_template(), raise_if_not_found=False)
        lang = False
        if template:
            lang = template._render_lang(self.ids)[self.id]
        if not lang:
            lang = get_lang(self.env).code
        compose_form = self.env.ref('account.account_invoice_send_wizard_form', raise_if_not_found=False)

        template_name = self.env.ref('fal_invoice_faktur_email.email_template_invoice')

        data = []

        # invoice_report_id = self.env.ref('account.report_invoice')
        pdf = self.env.ref('fal_tranindo_ext.action_tranindo_invoice_letter')._render_qweb_pdf(self.id)[0]
        pdf = base64.b64encode(pdf).decode()
        ir_values = {
            'name': 'Invoice Report.pdf',
            'type': 'binary',
            'datas': pdf,
            # 'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'account.move',
        }
        values_ir = self.env['ir.attachment'].create(ir_values)
        data.append(values_ir.id)
        
        if self.faktur_file_name:
            
            # pdf
            
            if self.faktur_file_name.endswith('.pdf'):
                faktur = {
                        'name': 'Faktur File.pdf',
                        'type': 'binary',
                        'datas': self.faktur_file,
                        # 'store_fname': data_record,
                        'res_model': 'account.move',
                    }
            
            # jpg
            
            elif self.faktur_file_name.endswith('.jpg'):
                faktur = {
                        'name': 'Faktur File.jpg',
                        'type': 'binary',
                        'datas': self.faktur_file,
                        # 'store_fname': data_record,
                        'res_model': 'account.move',
                    }
            
            # csv

            elif self.faktur_file_name.endswith('.csv'):
                faktur = {
                        'name': 'Faktur File.csv',
                        'type': 'binary',
                        'datas': self.faktur_file,
                        # 'store_fname': data_record,
                        'res_model': 'account.move',
                    }
            
            # zip

            elif self.faktur_file_name.endswith('.zip'):
                faktur = {
                        'name': 'Faktur File.zip',
                        'type': 'binary',
                        'datas': self.faktur_file,
                        # 'store_fname': data_record,
                        'res_model': 'account.move',
                    }
            
            # doc

            elif self.faktur_file_name.endswith('.doc'):
                faktur = {
                        'name': 'Faktur File.doc',
                        'type': 'binary',
                        'datas': self.faktur_file,
                        # 'store_fname': data_record,
                        'res_model': 'account.move',
                    }
            
            # docx

            elif self.faktur_file_name.endswith('.docx'):
                faktur = {
                        'name': 'Faktur File.docx',
                        'type': 'binary',
                        'datas': self.faktur_file,
                        # 'store_fname': data_record,
                        'res_model': 'account.move',
                    }
            
            # xls

            elif self.faktur_file_name.endswith('.xls'):
                faktur = {
                        'name': 'Faktur File.xls',
                        'type': 'binary',
                        'datas': self.faktur_file,
                        # 'store_fname': data_record,
                        'res_model': 'account.move',
                    }
            
            # xlsx

            elif self.faktur_file_name.endswith('.xlsx'):
                faktur = {
                        'name': 'Faktur File.xlsx',
                        'type': 'binary',
                        'datas': self.faktur_file,
                        # 'store_fname': data_record,
                        'res_model': 'account.move',
                    }

            # rar

            elif self.faktur_file_name.endswith('.rar'):
                faktur = {
                        'name': 'Faktur File.rar',
                        'type': 'binary',
                        'datas': self.faktur_file,
                        # 'store_fname': data_record,
                        'res_model': 'account.move',
                    }

            faktur_id = self.env['ir.attachment'].create(faktur)

            data.append(faktur_id.id)

        if self.po_file_name:
            if self.po_file_name.endswith('.pdf'):
                purchase = {
                        'name': 'PO File.pdf',
                        'type': 'binary',
                        'datas': self.po_file,
                        # 'datas_fname': 'Purchase Report',
                        'res_model': 'account.move',
                    }
            else:
                purchase = {
                        'name': 'PO File.jpg',
                        'type': 'binary',
                        'datas': self.po_file,
                        # 'datas_fname': 'Purchase Report',
                        'res_model': 'account.move',
                    }
            purchase_id = self.env['ir.attachment'].create(purchase)

            data.append(purchase_id.id)

        if self.surat_jalan_file_upload_name:
            if self.surat_jalan_file_upload_name.endswith('.pdf'):
                surat_jalan = {
                        'name': 'Surat Jalan File.pdf',
                        'type': 'binary',
                        'datas': self.surat_jalan_file_upload,
                        # 'datas_fname': 'Surat Jalan',
                        'res_model': 'account.move',
                    }
            else:
                surat_jalan = {
                        'name': 'Surat Jalan File.jpg',
                        'type': 'binary',
                        'datas': self.surat_jalan_file_upload,
                        # 'datas_fname': 'Surat Jalan',
                        'res_model': 'account.move',
                    }
            surat_jalan_id = self.env['ir.attachment'].create(surat_jalan)

            data.append(surat_jalan_id.id)

        ctx = dict(
            default_model='account.move',
            default_res_id=self.id,
            # For the sake of consistency we need a default_res_model if
            # default_res_id is set. Not renaming default_model as it can
            # create many side-effects.
            default_res_model='account.move',
            default_use_template=bool(template),
            default_template_id=template_name and template_name.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="mail.mail_notification_paynow",
            model_description=self.with_context(lang=lang).type_name,
            force_email=True,
            default_attachment_ids = data,
        )
        return {
            'name': _('Send Invoices'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    # @api.constrains('faktur_file_name', 'po_file_name', 'surat_jalan_file_upload_name')
    # def _check_type_faktur_file_name(self):
    #     for record in self:
    #         #list = ['.docx','.epub','.xlsx','.mp4','.mp3','.xls''.zip','.rar','.txt','.mkv']
    #         list = ['.png','.jpeg','.jpg','.csv']
            
    #         if record.state == 'posted':
    #             if record.move_type == 'out_invoice' and not any(record.po_file_name.endswith(s) for s in list):
    #                 raise ValidationError(_('One of your file is not *.jpg or Image(*.png,*.jpeg,*.jpg) type, please change your filetype!!!'))


    @api.constrains('faktur_file_name', 'po_file_name', 'surat_jalan_file_upload_name')
    def _check_type_faktur_file_name(self):
        for record in self:
            list = ['.docx','.epub','.xlsx','.mp4','.mp3','.xls''.zip','.rar','.txt','.mkv']
            # list = ['.png','.jpeg','.jpg']
            
            if record.state == 'posted':

                if record.move_type == 'out_invoice' and record.po_file_name in list:
                    raise ValidationError(_('One of your file is not *.jpg or Image(*.png,*.jpeg,*.jpg) type, please change your filetype!!!'))



    # @api.constrains('faktur_file_name', 'po_file_name', 'surat_jalan_file_upload_name')
    # def _check_type_faktur_file_name(self):
    #     for record in self:
    #         allowed_extensions = ['.png', '.jpeg', '.jpg']
            
    #         if record.state == 'posted' and record.move_type == 'out_invoice':
    #             # if isinstance(record.po_file_name, str):
    #             #     raise ValidationError(_('File name should be a string!'))
                
    #             if not any(record.po_file_name.endswith(s) in allowed_extensions):
    #                 raise ValidationError(_('One of your files is not a *.jpg or Image (*.png, *.jpeg, *.jpg) type. Please change the file type!'))
