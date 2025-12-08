from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    associated_trademark_ids = fields.One2many(
        "res.partner.trademark", "partner_id", string="Associated Trademarks"
    )

    trademark_history_ids = fields.One2many(
        "trademark.history",
        "partner_id",
        string="Trademark History"
    )

    label_ids = fields.One2many(
        "res.partner.label", "partner_id", string="Labels"
    )
    
    copyright_ids = fields.One2many(
        "res.partner.copyright", "partner_id", string="Copy-right"
    )