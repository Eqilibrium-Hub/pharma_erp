from odoo import models, fields, api


class EmployeeSamplingAndGiftReportingLine(models.Model):
    _name = 'setu.pharma.stock.distribution.line'
    _description = "Records Of Stock Distribution For Sample or Gifted Products Line"

    employee_id = fields.Many2one("hr.employee", string="Employee")
    distribution_date = fields.Date(related="distribution_id.distribution_date",
                                    string="Distribution date")
    product_id = fields.Many2one("product.product", string="Product")
    quantity = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Float(string="Price")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal")
    distribution_id = fields.Many2one("setu.pharma.stock.distribution", string="Distribution")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            line.price_unit = line.product_id.standard_price or line.price_unit

    @api.depends('product_id', 'quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit or line.subtotal
