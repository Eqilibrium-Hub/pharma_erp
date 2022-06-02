from datetime import datetime, date
from odoo import api, fields, models
from odoo.exceptions import UserError


class PharmaIncentive(models.Model):
    _name = "setu.pharma.incentive.structure"
    _description = "Employee Incentive"

    name = fields.Char('Name', help="Incentive Structure Name")
    division_id = fields.Many2one('setu.pharma.division', string="Division",
                                  help="Select Division To Give Targets")
    headquarter_id = fields.Many2one('setu.pharma.headquarters', string="Headquarter",
                                     help="Select Headquarter To Give Targets")
    designation_id = fields.Many2one('setu.pharma.designation', string="Designation",
                                     help="Select Designation To Give Targets")
    target_ids = fields.One2many('setu.pharma.incentive.structure.lines', 'incentive_id')


