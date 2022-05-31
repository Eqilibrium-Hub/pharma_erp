from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil import relativedelta
from odoo.exceptions import AccessError, UserError, AccessDenied


class StockistMonthlyStatement(models.Model):
    _name = 'setu.stockist.monthly.statement'
    _rec_name = 'partner_id'
    _description = "Stockist Statement"

    def _get_fiscal_period(self):
        fiscal_period_id = self.env['setu.pharma.fiscalyear'].search(
            [('start_year', '=', datetime.now().year)]).period_ids.filtered(
            lambda x: x.name == datetime.now().strftime('%B') or x.name == (
                (datetime.now() - relativedelta.relativedelta(months=1)).strftime('%B'))).mapped(
            'id')
        domain = [('id', 'in', fiscal_period_id)]
        return domain

    partner_id = fields.Many2one("res.partner", string="Partner")
    fiscal_period_id = fields.Many2one("setu.pharma.fiscalperiod", string="Fiscal Period",
                                       domain=_get_fiscal_period)
    previous_month_total_sales_amount = fields.Float("Previous Sales Amount",
                                                     compute="_compute_value")
    closing_month_total_sales_amount = fields.Float("Closing Sales Amount",
                                                    compute="_compute_amount")
    next_month_order_total = fields.Float("Next month order total", compute="_compute_amount")
    stockist_monthly_statement_ids = fields.One2many('setu.stockist.monthly.statement.line',
                                                     'stockist_monthly_statement_id')
    sale_order_id = fields.Integer("sale_order_id")
    division_id = fields.Many2one('setu.pharma.division', string='Division')
    headquarter_id = fields.Many2one('setu.pharma.headquarters', string="Headquater")
    difference_of_order = fields.Float('Difference', compute="_compute_difference")
    company_id = fields.Many2one("res.company", string="Company",
                                 default=lambda self: self.env.company)

    @api.constrains('fiscal_period_id')
    def check_fiscal_period(self):
        for record in self:
            fiscal_period = self.env['setu.stockist.monthly.statement'].search(
                [('partner_id', '=', self.env.context.get('active_id')),
                 ('id', '!=', record.id)]).mapped('fiscal_period_id').mapped('id')
            if record.fiscal_period_id.id in fiscal_period:
                raise UserError(_('Can not create two statements for any month.'))

    @api.model
    def default_get(self, vals):
        result = super(StockistMonthlyStatement, self).default_get(vals)
        fiscal_year = self.env['setu.pharma.fiscalyear'].search(
            [('start_year', '=', datetime.now().year)])
        division = self.env['hr.employee'].search([('name', '=', self.env.user.name)])
        fiscal_period = self.env['setu.stockist.monthly.statement'].search(
            [('partner_id', '=', self.env.context.get('active_id'))]).mapped(
            'fiscal_period_id').mapped('name')
        if datetime.now().strftime('%B') in fiscal_period:
            raise UserError(_('Can not create two statements for any month.'))
        else:
            result.update({'partner_id': self.env.context.get('active_id'),
                           'fiscal_period_id': (
                               fiscal_year.period_ids.filtered(
                                   lambda x: x.name == datetime.now().strftime('%B'))).id,
                           'stockist_monthly_statement_ids': [(0, 0, {'product_id': p.id}) for p in
                                                              division.division_id.product_ids],
                           'division_id': division.division_id.id,
                           'headquarter_id': division.headquarter_id.id
                           })
        return result

    def _compute_value(self):
        self.previous_month_total_sales_amount = 0
        for record in self._origin:
            statement = self.env['setu.stockist.monthly.statement'].search(
                [('partner_id', '=', record.partner_id.id),
                 ('id', '<', record.id)], limit=1,
                order='id desc')
            if statement:
                sale_amount = statement.stockist_monthly_statement_ids.mapped('sales_amount')
                record.previous_month_total_sales_amount = sum(sale_amount)
            else:
                record.previous_month_total_sales_amount = 0

    @api.depends('stockist_monthly_statement_ids')
    def _compute_amount(self):
        for record in self:
            record.closing_month_total_sales_amount = sum(
                record.stockist_monthly_statement_ids.mapped('sales_amount'))
            record.next_month_order_total = sum(
                record.stockist_monthly_statement_ids.mapped('next_month_order_value'))

    def sale_order_creation(self):
        # TODO: If we change sale order line then the price will be default product price not the stockiest price.
        sale_order = False
        for record in self.stockist_monthly_statement_ids.filtered(
                lambda x: x.next_month_order_qty):
            if record and not sale_order:
                sale_order = self.env['sale.order'].create({
                    'partner_id': self.partner_id.id,
                    'date_order': record.stockist_monthly_statement_id.fiscal_period_id.start_date + relativedelta.relativedelta(
                        months=1)
                })

            sale_order.write({
                'order_line': [(0, 0, {
                    'product_id': record.product_id.id,
                    'product_uom_qty': record.next_month_order_qty,
                    'price_unit': record.product_id.price_to_stockist,
                    'price_subtotal': record.next_month_order_qty * record.product_id.price_to_stockist
                })]
            })

            record.stockist_monthly_statement_id.sale_order_id = sale_order.id

    def action_view_sale_order(self):
        sale_id = self.sale_order_id
        action = self.env["ir.actions.actions"]._for_xml_id(
            "setu_pharma_basic.action_setu_sale_order")
        action['domain'] = [('id', '=', sale_id)]
        return action

    def _compute_difference(self):
        for record in self:
            sale_order = sum(self.env['sale.order'].search(
                [('id', '=', record.sale_order_id), ('state', '=', 'sale')]).order_line.mapped(
                'price_subtotal'))
            record.difference_of_order = sale_order - record.next_month_order_total
