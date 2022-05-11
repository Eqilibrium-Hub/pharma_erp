from odoo import models, fields, api, _


class SaleOrderExtends(models.Model):
    _inherit = 'sale.order'

    is_gift_order = fields.Boolean("Gift order ?", copy=False)
    is_sample_order = fields.Boolean("Sample order ?", copy=False)
    division_id = fields.Many2one('setu.pharma.division')

    @api.model
    def create(self, vals):
        """
        Added By: Mitrarajsinh Jadeja | Date: 29th Apr,2021
        Use: Assign Division in the Sale order
        """
        res = super(SaleOrderExtends, self).create(vals)
        context = self.env.context
        division_id = context.get('division_id', False)
        if division_id:
            res.update({'division_id': division_id})
        return res
