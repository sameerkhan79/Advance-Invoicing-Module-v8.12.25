from odoo import models, fields, api, _

class ResPartnerTrademark(models.Model):
    _name = "res.partner.label"
    _description = "Partner Trademark"
    _order = "sequence, id"
    _rec_name = "label"
    
    
    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one("res.partner", string="Partner", ondelete="cascade")
    label= fields.Char(string="Label", required=True)
    
    @api.model
    def create(self, vals):
        """Auto-fill partner name if coming from Partner form context"""
        if not vals.get("partner_id") and self.env.context.get("default_partner_id"):
            vals["partner_id"] = self.env.context["default_partner_id"]
        return super().create(vals)
