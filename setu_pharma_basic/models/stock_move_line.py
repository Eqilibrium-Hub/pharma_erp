from odoo import fields, models


class StackMoveLine(models.Model):
    _inherit = 'stock.move.line'

    headquarter_id = fields.Many2one(related='move_id.sale_line_id.order_id.headquarter_id',
                                     string='Headquarter')
    division_id = fields.Many2one(related='move_id.sale_line_id.order_id.division_id',
                                  string='Division')
