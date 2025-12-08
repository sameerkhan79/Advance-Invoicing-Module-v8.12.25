# models/account_move_line.py
from odoo import models, api, _ , fields
from odoo.exceptions import UserError
import json
from odoo.tools import format_date
from odoo.tools.misc import formatLang
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move.line'

    
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Service',
        inverse='_inverse_product_id',
        ondelete='restrict',
        check_company=True,
    )
    extra_flags = fields.Json("Extra Flags", default=dict)
    
    product_template_id = fields.Many2one(
        string="Classes",
        comodel_name='product.template',
        compute='_compute_product_template_id',
        search='_search_product_template_id',
        )
    attachment_name = fields.Char(string="Filename")
    logo_attachment_id = fields.Binary(string="Logo",help="Upload Logo of the required service!!!")
    country_id = fields.Many2one(string="Country", comodel_name='res.country', help="Country for which this logo is available")
    city_selection = fields.Selection(
        selection=[
            ('lahore', 'Lahore'),
            ('karachi', 'Karachi'),
            ('islamabad', 'Islamabad'),
        ],
        default='karachi',
        string="City",
    )
    opposition_number = fields.Json(
        string="Opposition Number (Class)",
        help="Stores mapping of classes → input value",
        store=True
    )
    appeal_number = fields.Json(
        string="Appeal Number (Class)",
        help="Stores mapping of classes → input value",
        store=True
    )
    suit_number = fields.Json(
        string="Suit Number (Class)",
        help="Stores mapping of classes → input value",
        store=True
    )
    filing_date= fields.Date(String="Filing Date")
    rectification_no = fields.Json(
        string="Rectification Number (Class)",
        help="Stores mapping of classes → input value",
        store=True
    )
    registration_no =fields.Json(
        string="Registration Number (Class)",
        help="Stores mapping of classes → input value",
        store=True
    )
    application_variant_data = fields.Json(
        string="Application Number (Class)",
        help="Stores mapping of classes → input value",
        store=True
    )
    selected_variant_ids = fields.Json(
        string='Selected Variants',
    )
    selected_variant_names = fields.Json(string="Variant Names", default=list)
    
    trademark_id = fields.Many2one(
        comodel_name="res.partner.trademark",
        string="Trademark",
        domain="[('partner_id', '=', parent.partner_id)]",
    )

    professional_fees = fields.Float(string="Professional Fees")
    service_fee = fields.Float(string="Service Fee",)
    fees_calculation = fields.Text(string="Fees Calculation", compute="_compute_professional_fees_expression", readonly=False, store=True)
    price_unit = fields.Float(string="Fees", help="Total Fees including Professional and Service Fees", compute="_compute_professional_fees_expression", store=True, readonly=False)
    offical_fees = fields.Float(string="Official Fees", compute="_compute_offical_fees",readonly=False, store=True)
    per_class_fee = fields.Float(string="Official Fees")
    miscellaneous_fees = fields.Float(string="Miscellaneous Fees", default=0.0)

    lenght_of_classes = fields.Integer(string="Number of Classes", default=0)
    
    discount_in_line = fields.Float(string="Discount")

    @api.depends('product_id','lenght_of_classes')
    def _compute_offical_fees(self):
        for rec in self:
            if rec.lenght_of_classes:
                rec.offical_fees = rec.per_class_fee
            else:
                rec.offical_fees = rec.product_id.lst_price

    label_id = fields.Many2one(
        comodel_name="res.partner.label",
        string="Label",
        domain="[('partner_id', '=', parent.partner_id)]",
        ondelete="set null"
    )

    # copyright field
    title_of_invention_id = fields.Many2one(
        comodel_name="res.partner.copyright",
        string="Title Of Invention",
        domain="[('partner_id', '=', parent.partner_id)]",
        ondelete="set null"
    )

    tax_amount = fields.Monetary(currency_field="currency_id",string="Tax Amount")

    @api.depends('professional_fees', 'lenght_of_classes','product_id', 'service_fee','offical_fees','tax_amount', 'miscellaneous_fees', 'discount_in_line')
    def _compute_professional_fees_expression(self):
        for rec in self:

            if rec.lenght_of_classes:
                total = rec.professional_fees * rec.lenght_of_classes
                per_class_total = rec.per_class_fee * rec.lenght_of_classes
                final_total = total + per_class_total
                rec.fees_calculation = (
                    f"({rec.professional_fees:,.2f} * {rec.lenght_of_classes}) + "
                    f"({rec.service_fee}) +"
                    f"({rec.per_class_fee:,.2f} * {rec.lenght_of_classes}) = {final_total:,.2f}"
                )
                rec.price_unit = final_total + (rec.service_fee or 0.0) + (rec.tax_amount or 0.0) + (rec.miscellaneous_fees or 0.0) - (rec.discount_in_line if rec.discount_in_line else 0.0)
            else:
                final_total = rec.professional_fees + rec.offical_fees
                rec.fees_calculation = (
                    f"{rec.professional_fees:,.2f} + {rec.service_fee} + {rec.offical_fees:,.2f} = {final_total:,.2f}"
                )
                rec.price_unit = final_total + (rec.service_fee or 0.0) + (rec.tax_amount or 0.0) + (rec.miscellaneous_fees or 0.0) - (rec.discount_in_line if rec.discount_in_line else 0.0)

    @api.depends('product_id')
    def _compute_product_template_id(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id

    def _search_product_template_id(self, operator, value):
        return [('product_id.product_tmpl_id', operator, value)]

    def update_price_unit(self, vals):
        """ Update price_subtotal of this account.move.line """
        self.ensure_one()  
        price = vals.get("price")
        variants = vals.get("selected_variant_ids",[])
        variants_names = vals.get("selected_variant_names",[])

        if price is None:
            raise UserError(_("No price provided"))

        try:
            price = float(price)
            varaint_price = float(vals.get('variant_price', 0.0))
        except ValueError:
            raise UserError(_("Invalid price value"))

        self.offical_fees = price
        self.per_class_fee = varaint_price
        self.selected_variant_ids = variants
        self.selected_variant_names = variants_names
        self.lenght_of_classes = len(variants_names) if variants_names else 0
        return {"status": "success", "new_price_subtotal": self.price_subtotal}
    
    def get_field_label(self, field_name):
        field = self._fields.get(field_name)
        if field:
            return field.string
        return field_name

    def get_field_value(self, field_name):
        """Return a display-ready value for a given field name"""
        field = self._fields.get(field_name)
        if not field:
            return ""

        value = getattr(self, field_name, False)
        if not value:
            return ""

        # Handle Many2one
        if field.type == "many2one":
            if field.name == "trademark_id" and value:
                return value.trademark_name
            if field.name == "product_template_id" and self.selected_variant_names:
                return ", ".join(self.selected_variant_names or [])
            return value.display_name
        
        if field.type == "many2many":
            if field.name == "tax_ids" and value:
                return ", ".join([f"{int(t.amount) if float(t.amount).is_integer() else t.amount}%" for t in value])

        
        # Handle Date / Datetime
        if field.type == "date":
            return format_date(self.env, value)
        if field.type == "datetime":
            return fields.Datetime.to_string(value)

        # Handle Binary (image/logo)
        if field.type == "binary":
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            mimetype = "image/png"  
            if hasattr(self, "logo_attachment_id") and self.attachment_name:
                if self.attachment_name.lower().endswith(".jpg") or self.attachment_name.lower().endswith(".jpeg"):
                    mimetype = "image/jpeg"
                elif self.attachment_name.lower().endswith(".gif"):
                    mimetype = "image/gif"
                elif self.attachment_name.lower().endswith(".svg"):
                    mimetype = "image/svg+xml"
            return f"data:{mimetype};base64,{value}"

        if isinstance(value, dict):
            return value

        if isinstance(value, (list, tuple)):
            return value
        
        if field.type == 'float':
            try:
                return formatLang(self.env, value, digits=2)
            except Exception:
                return "{:,.2f}".format(value)

        return str(value)

