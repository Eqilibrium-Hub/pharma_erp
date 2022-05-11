from odoo import models, fields


class StockLocationExtends(models.Model):
    _inherit = 'stock.location'

    employee_id = fields.Many2one("hr.employee", string="Employee")
    headquarter_id = fields.Many2one("setu.pharma.headquarters", string="Headquarter")
    division_id = fields.Many2one("setu.pharma.division", string="Division")
