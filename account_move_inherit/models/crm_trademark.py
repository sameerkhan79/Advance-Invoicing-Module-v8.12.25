from odoo import api, fields, models, _

class ResPartnerTrademark(models.Model):
    _name = "res.partner.trademark"
    _description = "Partner Trademark"
    _order = "sequence, id"
    _rec_name = "trademark_name"
    
    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one("res.partner", string="Partner", ondelete="cascade")
    
    trademark_name = fields.Char(string="Trademark Name")
    trademark_number = fields.Char(string="Trademark Number")
    name = fields.Char(string="Display Name")  
    trademark_price = fields.Float(string="Trademark Price", default=0.0)
    @api.model
    def create(self, vals):
        """Auto-fill partner name if coming from Partner form context"""
        if not vals.get("partner_id") and self.env.context.get("default_partner_id"):
            vals["partner_id"] = self.env.context["default_partner_id"]
        return super().create(vals)
