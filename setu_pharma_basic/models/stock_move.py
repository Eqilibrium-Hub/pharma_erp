from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    division_id = fields.Many2one(related='sale_line_id.order_id.division_id', string='Division')
    headquarter_id = fields.Many2one(related='sale_line_id.order_id.headquarter_id', string='Headquarter')
