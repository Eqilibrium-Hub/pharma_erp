from datetime import datetime, date
from odoo import api, fields, models
from odoo.exceptions import UserError


class PharmaIncentiveLines(models.Model):
    _name = "setu.pharma.incentive.structure.lines"
    _description = "Employee Incentive"

    incentive_id = fields.Many2one('setu.pharma.incentive.structure')
    target_id = fields.Many2one('setu.pharma.sales.target', string="Target Name",
                                domain="[('status', '!=', 'expired')]")
    target_based_on = fields.Char("Target Based on", compute="_compute_target_based_on")
    fiscal_period = fields.Selection(related="target_id.fiscal_period")
    reward_type = fields.Selection(related="target_id.reward_type")
    status = fields.Selection(related="target_id.status")

    @api.depends('target_id')
    def _compute_target_based_on(self):
        """ To Get Target Based On Product Or Sales Amount"""
        for record in self:
            if record.target_id.based_on_product:
                record.target_based_on = 'Product Based'
            elif record.target_id.based_on_sales:
                record.target_based_on = 'Sales Amount Based'
            elif record.target_id.based_on_product and record.target_id.based_on_sales:
                record.target_based_on = 'Target Based On Product And Sales Amount'
            else:
                record.target_based_on = ''
