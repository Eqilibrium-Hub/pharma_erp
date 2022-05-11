from odoo import fields, models, api


class PersonalOrderBookingLine(models.Model):
    _name = 'setu.pharma.pob.line'
    _description = "Personal Order Booking Line"

    product_id = fields.Many2one("product.product", string="Product")
    quantity = fields.Float(string="Quantity", default=1)
    pob_id = fields.Many2one("setu.pharma.pob", string="POB")
    price_unit = fields.Float(string="Price")
    subtotal = fields.Float(string="Subtotal", compute='_compute_subtotal')

    @api.depends('product_id', 'quantity', 'price_unit')
    def _compute_subtotal(self):
        for pob_line in self:
            if pob_line.product_id:
                pob_line.subtotal = pob_line.quantity * pob_line.price_unit
            else:
                pob_line.subtotal = pob_line.subtotal
