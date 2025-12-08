# my_module/controllers/main.py
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError, ValidationError, AccessError
class ProductVariantController(http.Controller):

    @http.route('/get_product_variants', type='json', auth='public', methods=['POST'], csrf=False)
    def get_product_variants(self, product_tmpl_id):
        if not product_tmpl_id:
            return []
        product = request.env['product.product'].sudo().search([
            ('product_tmpl_id', '=', product_tmpl_id)
        ])
        
        product_detail=product.attribute_line_ids.mapped('attribute_id').ids
        variants = request.env['product.template.attribute.value'].sudo().search([('attribute_id','in', product_detail)])
        # if not variants:
        #     raise ValidationError("No variants found for the given product template ID.")
        return [
            {   
                "product_image": product.image_1920,
                'product_id': product.id,
                'product_name': product.name,
                'id': v.id,
                "name": v.name,
                "price": v.price_extra,
                "attribute_id": v.attribute_id.id,
                "attribute_name": v.attribute_id.name,
            }
            for v in variants
        ]
