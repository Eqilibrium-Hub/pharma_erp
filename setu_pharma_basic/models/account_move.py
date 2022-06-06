from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    division_id = fields.Many2one('setu.pharma.division', 'Division')
    headquarter_id = fields.Many2one('setu.pharma.headquarters', 'Headquarter')
