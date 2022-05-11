from odoo import fields, models


class ExpenseConfigurator(models.Model):
    _name = 'hr.expense.configurator'
    _description = "For Expense Configurator of pharma company "

    name = fields.Char(string="Name")
    expense_type_id = fields.Many2one('hr.expense.type', string="Expense Type")
    designation_ids = fields.Many2many('setu.pharma.designation', string="Designations")
    division_id = fields.Many2one('setu.pharma.division', string="Division")
    headquarter_ids = fields.Many2many(comodel_name='setu.pharma.headquarters',
                                       relation='hr_expense_configurator_setu_pharma_headquarter_rel',
                                       column1='configurator_id', column2='headquarter_id', string="Headquarters")
    calculation_type = fields.Selection([('fixed', 'Fixed'),
                                         ('actual', 'Actual'),
                                         ('distance', 'Distance')], string="Calculation pattern")
    distance_range_ids = fields.One2many('hr.expense.distance.range.payment', 'expense_configurator_id',
                                         string="Distance range")
    fixed_amount = fields.Float(string="Amount")
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
