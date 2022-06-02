from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PharmaSalesTarget(models.Model):
    _name = "setu.pharma.sales.target"
    _description = "Sales Target"

    name = fields.Char("Name", help="Target Name")
    based_on_product = fields.Boolean('Product Based')
    based_on_sales = fields.Boolean('Sales Amount')
    target_amount = fields.Float("Target Amount", help="Target Amount For Sales Target")
    incentive_amount = fields.Float("Incentive Amount", help="Incentive Amount For Sale Target")
    incentive_percentage = fields.Float("Incentive Percentage", help="Incentive Percentage For Sales Target")
    target_percentage_for_quarter = fields.Float("Target Percentage", help="Target Percentage For Quarter's Next Month")
    fiscal_period = fields.Selection(selection=[
                                    ('monthly', 'Monthly'),
                                    ('quarterly', 'Quarterly'),
                                    ('quarterly+1', 'Quarterly+1'),
                                    ('yearly', 'Yearly')],
                                    string='Fiscal Period', help="To Select Incentive Periods")
    sales_based_on = fields.Selection(selection=[
                                    ('secondary_sales', 'Secondary Sales'),
                                    ('primary_sales', 'Primary Sales')])
    reward_type = fields.Selection(selection=[
                    ('fixed_amount', 'Fixed Amount'), ('based_on_percentage', 'Based On Percentage'),
                   ('international_trip', 'International Trip'), ('domestic_trip', 'Domestic Trip'),
                   ('international_domestic_trip', 'International+Domestic Trip'),
                   ('based_on_range', 'Based On Range')],
                    help="Select Reward Type To Give Rewards To Employees")
    status = fields.Selection([
                    ('draft', 'Draft'),
                    ('running', 'Running'),
                    ('expired', 'Expired')],
                    readonly="True", default='draft')
    target_product_lines_ids = fields.One2many('setu.pharma.target.product.lines',
                                               'target_id',
                                               help="Focused Products For Target")
    range_ids = fields.One2many('setu.sales.range',
                                'target_id',
                                help="Sales Range For Incentive")
    fiscal_month_ids = fields.Many2many('setu.pharma.fiscalperiod',
                                        string="Fiscal Months",
                                        help="Select Months To Give Rewards ")
    incentive_structure_id = fields.Many2one('setu.pharma.incentive.structure')
    target_end_date = fields.Date("Target End Date", compute="_compute_target_date")
    target_start_date = fields.Date("Target Start Date", compute="_compute_target_date")
    message = fields.Html(compute='_compute_message')

    @api.depends('fiscal_month_ids')
    def _compute_target_date(self):
        """
            Generate Status Of Target Based On Fiscal Months
        """
        self.target_end_date = ''
        self.target_start_date = ''
        for record in self:
            if record.fiscal_month_ids:
                record.target_start_date = record.fiscal_month_ids.search([('name', '=',
                    min(sorted(record.fiscal_month_ids.mapped('name'),
                    key=lambda m: datetime.strptime(m, "%B"))))]).start_date
                record.target_end_date = record.fiscal_month_ids.search([('name', '=',
                    max(sorted(record.fiscal_month_ids.mapped('name'),
                    key=lambda m: datetime.strptime(m, "%B"))))]).end_date

                current_date = datetime.now().date()

                if current_date >= record.target_start_date and current_date <= record.target_end_date:
                    record.status = "running"
                elif current_date > record.target_end_date:
                    record.status = "expired"
                else:
                    record.status = "draft"

    @api.onchange('based_on_product', 'based_on_sales')
    def _onchange_based_on_product(self):
        """ If Target Is Based On Product Than Reward Type Is Fixed Amount """
        if self.based_on_product:
            self.reward_type = 'fixed_amount'

    @api.depends('based_on_product', 'based_on_sales', 'incentive_amount', 'incentive_percentage', 'target_amount',
                 'target_product_lines_ids.incentive_amount_per_quantity')
    def _compute_message(self):
        """
            Generates Message For Employee's Reward Based On Target Conditions
        """
        self.message = ''
        for record in self:

            if record.reward_type == 'based_on_percentage':
                incentive = str(record.incentive_percentage) + "% Incentive Of Sales Amount"
            elif record.reward_type == 'fixed_amount':
                incentive = str(record.incentive_amount) + " Incentive Amount"
            elif record.reward_type == 'international_trip':
                incentive = " International Trip"
            elif record.reward_type == 'domestic_trip':
                incentive = " Domestic Trip"
            elif record.reward_type == 'international_domestic_trip':
                incentive = " International Trip And Domestic Trip"
            else:
                incentive = ''

            months = ','.join(map(str, record.fiscal_month_ids.mapped('name')))
            total = str(sum(record.target_product_lines_ids.mapped('total_incentive_amount')))

            if record.based_on_sales and not record.reward_type == 'based_on_range':
                record.message = "If You Achieve The Target Of Amount <b><font color='#1f1f1f'>" + \
                                 str(record.target_amount) + "</font></b> In <b><font color='#1f1f1f'>" \
                                 + months + "</font></b>.<br> You Will Get <b><font color='#1f1f1f' >" + \
                                 incentive + "</font></b>."
            elif record.reward_type == 'based_on_range' and record.based_on_sales:
                message = ''
                for range in record.range_ids:
                    message += "If You Achieve Target Between <b><font color='#1f1f1f'>" + \
                               str(range.range_from) + "</font></b> To <b><font color='#1f1f1f'>" + \
                               str(range.range_to) + "</font></b>.<br> You Will Get <b><font color='#1f1f1f'>" + \
                               str(range.incentive_percentage) + "</font></b>% Incentive.<br>"
                record.message = message

            if record.based_on_product:
                record.message += "If You Achieve The Target Of Below Products You Will Get " + total

    # @api.constrains('fiscal_month_ids')
    # def _check_fiscal_months(self):
        """ Note: This Code is for fiscal_months restrictions and commented because of Currently We Can't Add Any Restrictions"""
    #   for record in self._origin:
    #         if record.fiscal_period == 'monthly' and len(record.fiscal_month_ids) != 1:
    #             raise UserError(_("Select Only One Month"))
    #         if (record.fiscal_period == 'quarterly' or record.fiscal_period == 'quarterly+1') and (len(
    #                 record.fiscal_month_ids) > 3 or len(
    #             record.fiscal_month_ids) < 3):
    #             raise UserError(_("Select Only Three Months"))
    #         if record.fiscal_month_ids:
    #             month_number = [datetime.strptime(x, '%B').month for x in record.fiscal_month_ids.mapped('name')]
    #             if sorted(month_number) == list(range(min(month_number), max(month_number) + 1)):
    #                 continue
    #             else:
    #                 raise UserError(_("Please Select Months Properly"))
    #     for month in record.fiscal_month_ids:
    #         if month.end_date < datetime.now().date():
    #             raise UserError(_("Can't Select Months Before Current Date"))
