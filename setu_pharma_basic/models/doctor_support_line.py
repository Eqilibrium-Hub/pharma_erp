from odoo import fields, models, api


class DoctorSupportLine(models.Model):
    _name = 'setu.pharma.monthly.doctor.support.line'
    _description = "Doctor Support Line for Pharma Companies"

    support_id = fields.Many2one("setu.pharma.monthly.doctor.support", string="Support")
    product_id = fields.Many2one("product.product", string="Product")
    quantity = fields.Float(string="Quantity", default=1.0)
    date = fields.Date(related="support_id.date", string="Date")
    price_unit = fields.Float(string="Price")
    sub_total = fields.Float(string='Sub Total', compute="_compute_sub_total")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            line.price_unit = line.product_id.standard_price or line.price_unit

    @api.depends('product_id', 'quantity', 'price_unit')
    def _compute_sub_total(self):
        for doc_sup_line in self:
            doc_sup_line.sub_total = doc_sup_line.quantity * doc_sup_line.price_unit or \
                                     doc_sup_line.sub_total
