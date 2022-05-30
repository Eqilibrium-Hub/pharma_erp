from odoo import models, fields


class SaleOrderExtends(models.Model):
    _inherit = 'sale.order'

    is_gift_order = fields.Boolean("Gift order ?", copy=False)
    is_sample_order = fields.Boolean("Sample order ?", copy=False)
    division_id = fields.Many2one('setu.pharma.division', 'Division')
