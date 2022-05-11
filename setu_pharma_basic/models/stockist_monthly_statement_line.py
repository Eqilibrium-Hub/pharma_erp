from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from datetime import datetime


class StockistMonthlyStatementLine(models.Model):
    _name = 'setu.stockist.monthly.statement.line'
    _rec_name = 'product_id'

    product_id = fields.Many2one("product.product", string="Product")
    product_price = fields.Float("Product Price", compute="_get_product_price")
    opening_stock = fields.Integer("Opening", compute="_compute_opening_stock")
    purchase = fields.Integer("Purchase", compute="_compute_purchase")
    purchase_amount = fields.Float("Purchase amount", compute="_compute_purchase")
    purchase_return = fields.Integer("Purchase return")
    purchase_return_amount = fields.Float("Purchase return amount")
    sales = fields.Integer("Sales")
    sales_amount = fields.Float("Sales amount")
    free_schema = fields.Integer("Free schema")
    sales_return = fields.Integer("Sales return")

    sales_return_amount = fields.Float("Sales return amount")
    closing = fields.Integer("Closing", compute="_compute_closing")
    closing_amount = fields.Float("Closing amount", compute="_compute_closing")
    next_month_order_qty = fields.Integer("Next month order qty", compute="_compute_next_order")
    next_month_order_value = fields.Float("Next month order value", compute="_compute_next_order")
    stockist_monthly_statement_id = fields.Many2one('setu.stockist.monthly.statement')
    free_schema_amount = fields.Float("Free Schema Amount")

    def _get_product_price(self):
        for rec in self:
            rec.product_price = rec.product_id.price_to_stockist

    def _compute_opening_stock(self):
        self.opening_stock = 0.0
        for record in self._origin:
            statement = self.env['setu.stockist.monthly.statement'].search(
                [('partner_id', '=', record.stockist_monthly_statement_id.partner_id.id),
                 ('id', '<', record.stockist_monthly_statement_id.id)], limit=1, order='create_date desc')
            if statement:
                for lines in statement.stockist_monthly_statement_ids:
                    if lines.product_id == record.product_id:
                        record.opening_stock = lines.closing
            else:
                record.opening_stock = 0.0

    @api.onchange('sales', 'sales_return', 'purchase_return')
    def _onchange_sales(self):
        for record in self:
            product = self.env['product.product'].search([('id', '=', record.product_id.id)])
            if record.sales <= record.purchase or record.sales <= record.opening_stock:
                record.sales_amount = record.sales * product.price_to_stockist
            else:
                record.sales_amount = 0
            record.sales_return_amount = record.sales_return * product.price_to_stockist
            record.purchase_return_amount = record.purchase_return * product.price_to_stockist

    @api.depends('sales', 'sales_return', 'purchase_return', 'purchase', 'closing', 'free_schema', 'opening_stock')
    def _compute_closing(self):
        self.closing = 0
        self.closing_amount = 0
        for record in self:
            product = self.env['product.product'].search([('id', '=', record.product_id.id)])
            total_purchase = (record.purchase - record.purchase_return) + record.opening_stock
            total_sales = record.sales - record.sales_return
            if total_purchase > 0 or record.opening_stock > 0:
                record.closing = (total_purchase - total_sales) - record.free_schema
                record.closing_amount = record.closing * product.price_to_stockist

    @api.depends('closing', 'next_month_order_qty', 'purchase_return', 'free_schema')
    def _compute_next_order(self):
        for record in self:
            product = self.env['product.product'].search([('id', '=', record.product_id.id)])
            record.next_month_order_qty = record.closing * 1.5
            record.next_month_order_value = record.next_month_order_qty * product.price_to_stockist
            record.free_schema_amount = record.free_schema * product.price_to_stockist

    @api.depends('purchase')
    def _compute_purchase(self):
        self.purchase = 0
        self.purchase_amount = 0
        for record in self:
            sale_order = self.env['sale.order'].search(
                [('partner_id', '=', record.stockist_monthly_statement_id.partner_id.id)])
            for sale in sale_order:
                if sale.date_order.strftime('%B') == record.stockist_monthly_statement_id.fiscal_period_id.name and sale.date_order.year == record.stockist_monthly_statement_id.fiscal_period_id.start_date.year:
                    for lines in sale.order_line:
                        if record.product_id == lines.product_id:
                            record.purchase += lines.product_uom_qty
                            record.purchase_amount = record.purchase * lines.product_id.price_to_stockist
