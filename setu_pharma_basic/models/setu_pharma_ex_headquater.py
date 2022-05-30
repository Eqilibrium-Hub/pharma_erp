from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.osv import expression


class SetuPharmaExHeadquarter(models.Model):
    _name = 'setu.pharma.ex.headquarter'
    _description = "Setu Pharma Ex. Headquarter"
    _rec_name = 'city_id'

    headquarter_id = fields.Many2one('setu.pharma.headquarters')
    state_id = fields.Many2one(related='headquarter_id.state_id', string="City", store=True)
    city_id = fields.Many2one('res.city', string="City",)
    distance = fields.Float(string="Distance")

    @api.constrains('city_id')
    def unique_city(self):
        for ex_headquater in self:
            if self.search(
                    [
                        ('id', '!=', ex_headquater.id),
                        ('city_id', '=', ex_headquater.city_id.id),
                        ('headquarter_id', '=', ex_headquater.headquarter_id.id)
                    ]):
                raise UserError(_('Ex. Headquarter must be unique !!!'))
