from odoo import fields, models

class City(models.Model):
    _inherit = "res.city"

    code = fields.Char(string="City Code", copy=False)
    headquarter_id = fields.Many2one(comodel_name='setu.pharma.headquarters',
                                     string=' Headquarter')

