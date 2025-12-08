from odoo import api, fields, models,tools
from odoo.exceptions import UserError

class AccountMoveSendWizard(models.TransientModel):
    _inherit = "account.move.send.wizard"

    mail_partner_ids = fields.Many2one(
        'res.partner', string='To', help='Partners to whom the email will be sent.',
        compute='_compute_mail_subject_body_partners', store=True, readonly=False
    )
    mail_partner_cc_ids = fields.Many2many(
        'res.partner', string='CC', help='Partners to be CCed on the email.',
        compute='_compute_mail_partners', store=True, readonly=False, required=False
    )


    @api.depends('mail_template_id', 'mail_lang')
    def _compute_mail_partners(self):
        for wizard in self:
            if wizard.mail_template_id:
                wizard.mail_subject = self._get_default_mail_subject(wizard.move_id, wizard.mail_template_id, wizard.mail_lang)
                wizard.mail_body = self._get_default_mail_body(wizard.move_id, wizard.mail_template_id, wizard.mail_lang)
                wizard.mail_partner_cc_ids = self._get_default_mail_partner_cc_ids(wizard.move_id, wizard.mail_template_id, wizard.mail_lang)
            else:
                wizard.mail_subject = wizard.mail_body = wizard.mail_partner_cc_ids = None


    def _get_sending_settings(self):

        self.ensure_one()
        send_settings= super()._get_sending_settings()

        if 'email' in send_settings['sending_methods']:
            send_settings.update({
                'mail_partner_cc_ids': self.mail_partner_cc_ids.ids,
            })
        return send_settings

class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    @api.model
    def _get_mail_params(self, move, move_data):
        # We must ensure the newly created PDF are added. At this point, the PDF has been generated but not added
        # to 'mail_attachments_widget'.
        mail_attachments_widget = move_data.get('mail_attachments_widget')
        seen_attachment_ids = set()
        to_exclude = {x['name'] for x in mail_attachments_widget if x.get('skip')}
        for attachment_data in self._get_invoice_extra_attachments_data(move) + mail_attachments_widget:
            if attachment_data['name'] in to_exclude and not attachment_data.get('manual'):
                continue

            try:
                attachment_id = int(attachment_data['id'])
            except ValueError:
                continue

            seen_attachment_ids.add(attachment_id)

        mail_attachments = [
            (attachment.name, attachment.raw)
            for attachment in self.env['ir.attachment'].browse(list(seen_attachment_ids)).exists()
        ]
        mail_params = {
            'author_id': move_data['author_partner_id'],
            'body': move_data['mail_body'],
            'subject': move_data['mail_subject'],
            'partner_ids': move_data['mail_partner_ids'],
            'attachments': mail_attachments,
        }
        cc_partners = move_data.get('mail_partner_cc_ids')
        if cc_partners:
            mail_params.update({'partner_cc_ids': cc_partners})

        # raise UserError(f"Mail params: {mail_params}")
        return mail_params
    
    @api.model
    def _send_mail(self, move, mail_template, **kwargs):
        # Extract CC and TO safely
        cc_partners = kwargs.pop('partner_cc_ids', [])
        to_partners = kwargs.pop('partner_ids', [])

        # Merge To + CC if you want them all notified
        if cc_partners:
            all_partners = list(set(to_partners) | set(cc_partners))
            # Call parent safely with single partner_ids
            new_message = super()._send_mail(
                move,
                mail_template,
                partner_ids=all_partners,
                **kwargs
            )
        else:
            new_message = super()._send_mail(
                move,
                mail_template,
                partner_ids=to_partners,
                **kwargs
            )
        return new_message

    @api.model
    def _get_default_sending_settings(self, move, from_cron=False, **custom_settings):
        # Call super to keep Odoo’s default behavior
        vals = super()._get_default_sending_settings(move, from_cron=from_cron, **custom_settings)

        if 'email' in vals['sending_methods']:
            mail_template = vals.get('mail_template') or self._get_default_mail_template_id(move)
            mail_lang = vals.get('mail_lang') or self._get_default_mail_lang(move, mail_template)

            vals.update({
                'mail_partner_cc_ids': custom_settings.get(
                    'mail_partner_cc_ids',
                ) or self._get_default_mail_partner_cc_ids(move, mail_template, mail_lang).ids,
            })

        return vals

        
    @api.model
    def _get_default_mail_partner_cc_ids(self, move, mail_template, mail_lang):
        partners = self.env['res.partner'].with_company(move.company_id)
        if mail_template.email_cc:
            email_cc = self._get_mail_default_field_value_from_template(mail_template, mail_lang, move, 'email_cc')
            for mail_data in tools.email_split(email_cc):
                partners |= partners.find_or_create(mail_data)
        return partners.filtered('email')
    
    @api.model
    def _get_default_mail_partner_ids(self, move, mail_template, mail_lang):
        partners = self.env['res.partner'].with_company(move.company_id)
        if mail_template.email_to:
            email_to = self._get_mail_default_field_value_from_template(mail_template, mail_lang, move, 'email_to')
            for mail_data in tools.email_split(email_to):
                partners |= partners.find_or_create(mail_data)
        return partners.filtered('email')