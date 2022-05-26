from odoo import fields, models, api
from ..tools.math_tools import minus_value_on_percentage


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_gift_product = fields.Boolean(string="Gift Product?")
    is_focus_product = fields.Boolean(string="Focus Product?")
    division_id = fields.Many2one("setu.pharma.division", string="Division")
    headquarter_id = fields.Many2one(comodel_name='setu.pharma.headquarters', string='Headquarter')
    price_to_stockist = fields.Monetary('Price To Stockist (PTS)', compute="_compute_pts",
                                        depends=['price_to_stockist_percentage', 'list_price'],
                                        store=True)
    price_to_stockist_percentage = fields.Float('PTS (%)')
    price_to_retailer = fields.Monetary('Price To Retailer (PTR)', compute="_compute_ptr",
                                        store=True,
                                        depends=['price_to_retailer_percentage', 'list_price'])
    price_to_retailer_percentage = fields.Float('PTR (%)')
    drug_contain_lines = fields.One2many('product.product.drug.contain', 'product_id',
                                         'Drug Contains')
    """ This method Set default value Of product trype"""
    @api.model
    def default_get(self, fields):
        res = super(ProductProduct, self).default_get(fields)
        res['detailed_type'] = 'product'
        return res

    def _compute_ptr(self):
        """ Calculate PTR (Price To Retailer) value based on percentage in Product."""
        for product in self:
            mrp = product.list_price
            ptr_percentage = product.price_to_retailer_percentage
            product.price_to_retailer = minus_value_on_percentage(mrp, ptr_percentage)

    def _compute_pts(self):
        """ Calculate PTS (Price To Stockist) value based on percentage in Product."""
        for product in self:
            mrp = product.list_price
            pts_percentage = product.price_to_stockist_percentage
            product.price_to_stockist = minus_value_on_percentage(mrp, pts_percentage)
