from odoo import fields, models


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    dcr_history_id = fields.Many2one('setu.pharma.employee.daily.call', string='Daily Call Report')