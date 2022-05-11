from odoo import models, fields


class StockPickingExtends(models.Model):
    _inherit = 'stock.picking'

    is_gift_order = fields.Boolean(string="Gift order ?")
    return_expired_stock = fields.Boolean(string="Return expired stock ?")
    return_damage = fields.Boolean(string="Return damage stock ?")
    is_sample_order = fields.Boolean(string="Sample order ?")
    headquarter_id = fields.Many2one('setu.pharma.headquarters', 'Headquarter')
