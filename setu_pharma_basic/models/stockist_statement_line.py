from odoo import fields, models


class StockistStatementLine(models.Model):
    _name = "setu.pharma.monthly.closing.process.line"
    _description = "Statement Line of Stockist"

    product_id = fields.Many2one("product.product", string="Product")
    sales_quantity = fields.Float(string="Sales")
    date = fields.Date(related="statement_id.date", string="Date")
    price_unit = fields.Float(string="Price")
    statement_id = fields.Many2one("setu.pharma.monthly.closing.process", string="Statement")
    closing_quantity = fields.Float(string="Closing")
