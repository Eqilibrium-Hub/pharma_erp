from odoo import models, fields, api


class StockPickingExtends(models.Model):
    _inherit = 'stock.picking'

    is_gift_order = fields.Boolean(string="Gift order ?")
    return_expired_stock = fields.Boolean(string="Return expired stock ?")
    return_damage = fields.Boolean(string="Return damage stock ?")
    is_sample_order = fields.Boolean(string="Sample order ?")
    headquarter_id = fields.Many2one('setu.pharma.headquarters', 'Headquarter')

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        for picking in self:
            picking.headquarter_id = picking.picking_type_id.warehouse_id.headquarter_id and picking.picking_type_id.warehouse_id.headquarter_id.id
