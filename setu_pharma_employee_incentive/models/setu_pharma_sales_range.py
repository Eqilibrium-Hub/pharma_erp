from datetime import datetime, date
from odoo import api, fields, models
from odoo.exceptions import UserError


class PharmaTargetProducts(models.Model):
    _name = "setu.sales.range"
    _description = "Sales Range"

    range_from = fields.Integer("From", help="Sales Range Start From")
    range_to = fields.Integer("To", help="Sales Range End To")
    incentive_percentage = fields.Float("Incentive Percentage", help="Incentive Percentage For Selected Sales Target Range")
    target_id = fields.Many2one('setu.pharma.sales.target')




