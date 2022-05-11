from odoo import fields, models


class ProductProductDrugContain(models.Model):
    _name = 'product.product.drug.contain'
    _description = "Drug Contains for Each Product"

    product_id = fields.Many2one('product.product', 'Product Name')
    name = fields.Char('Drug Name')
    amount = fields.Float('Drug Amount')
    drug_uom = fields.Many2one('uom.uom', 'Drug UOM',
                               default=lambda self: self.env.ref(
                                   'setu_pharma_basic.product_uom_milligram',
                                   raise_if_not_found=False))
