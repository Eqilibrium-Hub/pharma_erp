from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    division_id = fields.Many2one('setu.pharma.division', 'Division')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    headquarter_id = fields.Many2one('setu.pharma.headquarters', 'Headquarter')
