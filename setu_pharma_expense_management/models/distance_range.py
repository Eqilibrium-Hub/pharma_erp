from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class DistanceRange(models.Model):
    _name = 'hr.expense.distance.range.payment'
    _description = "Range of distance"
    _order = 'distance_range asc'

    distance_range = fields.Float(string="Distance Range")
    designation_ids = fields.Many2many(comodel_name='setu.pharma.designation',
                                       relation="expense_distance_range_pharma_designation_rel",
                                       column1='distance_id', column2='designation_id', string="Designations")
    amount = fields.Float(string="Amount")
    expense_configurator_id = fields.Many2one('hr.expense.configurator', string="Expense Configurator", )
