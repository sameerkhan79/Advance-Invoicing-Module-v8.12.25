from odoo import models, fields, _, api
from odoo.exceptions import AccessError
class TrademarkHistory(models.Model):
    _name = "trademark.history"
    _description = "Trademark History"
    _order = "sequence, id"
    _rec_name = "name"

    sequence = fields.Integer(default=10)

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=True,
        ondelete="cascade",
    )

    name = fields.Char(string="Case Name")
    services_taken = fields.Many2one('product.product',string="Services Taken")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    add_file = fields.Binary(string="Attached File")
    add_file_filename = fields.Char(string="File Name")
    case_description = fields.Text(string="Case Description")
    label = fields.Char(string="Label")
    trademark_id = fields.Many2one(
        "res.partner.trademark",
        string="Trademark",
        domain="[('partner_id', '=', partner_id)]",
    )

    currency_id = fields.Many2one("res.currency", string="Currency")
    fee_per_class = fields.Monetary(string="Fee Per Class", currency_field="currency_id")
    total_fee = fields.Monetary(string="Total Fee", currency_field="currency_id")

    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
        ],
        string="Status",
        default="draft",
    )

    @api.onchange("trademark_id")
    def _onchange_trademark_id(self):
        if self.trademark_id:
            self.partner_id = self.trademark_id.partner_id

    def write(self, vals):
        """ Restrict reverting from Done unless user is a Trademark Manager """
        if "status" in vals:
            for rec in self:
                if rec.status == "done" and vals["status"] in ("draft", "in_progress"):
                    if not self.env.user.has_group("account_move_inherit.group_trademark_manager"):
                        raise AccessError(
                            _("Only Trademark Managers can revert status from Done.")
                        )
        return super().write(vals)