from datetime import datetime, date
from odoo import api, fields, models
from odoo.exceptions import UserError


class PharmaTargetProducts(models.Model):
    _name = "setu.pharma.target.product.lines"
    _description = "Sales Target Products"

    product_id = fields.Many2one('product.product', help="Targeted Product")
    product_qty = fields.Integer("Product Quantity", help="Target Quantity of Product")
    product_amount = fields.Float("Product price", compute="_get_product_price", help="Product's Price Related To Price To Stockist")
    incentive_amount_per_quantity = fields.Float("Incentive Amount", help="Incentive Amount For Product Per Unit/Quantity")
    total_incentive_amount = fields.Float("Total Incentive Amount", help=" Total Incentive Amount For Product")
    target_id = fields.Many2one('setu.pharma.sales.target')

    @api.depends('product_id')
    def _get_product_price(self):
        for rec in self:
            rec.product_amount = rec.product_id.price_to_stockist

