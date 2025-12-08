from odoo import models, fields, api, _

class ResPartnerTrademark(models.Model):
    _name = "res.partner.copyright"
    _description = "Copy Right Details"
    _order = "sequence, id"
    _rec_name = "copyright"
    
    
    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one("res.partner", string="Partner", ondelete="cascade")
    copyright = fields.Char(string="Copy-right", required=True)
    
    @api.model
    def create(self, vals):
        """Auto-fill partner name if coming from Partner form context"""
        if not vals.get("partner_id") and self.env.context.get("default_partner_id"):
            vals["partner_id"] = self.env.context["default_partner_id"]
        return super().create(vals)
