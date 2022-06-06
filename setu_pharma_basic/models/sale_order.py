from odoo import models, fields, api


class SaleOrderExtends(models.Model):
    _inherit = 'sale.order'

    is_gift_order = fields.Boolean("Gift order ?", copy=False)
    is_sample_order = fields.Boolean("Sample order ?", copy=False)
    division_id = fields.Many2one('setu.pharma.division', 'Division')
    headquarter_id = fields.Many2one('setu.pharma.headquarters', 'Headquarter')

    @api.onchange('warehouse_id')
    def onchange_warehouse(self):
        """
        This method set warehose
        """
        for res in self:
            res.division_id = res.warehouse_id.division_id.id
            res.headquarter_id = res.warehouse_id.headquarter_id.id

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrderExtends, self)._prepare_invoice()
        invoice_vals.update({'division_id': self.division_id.id, 'headquarter_id': self.headquarter_id.id})
        return invoice_vals
