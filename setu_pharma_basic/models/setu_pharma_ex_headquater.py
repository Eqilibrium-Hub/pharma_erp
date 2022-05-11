from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SetuPharmaExHeadquarter(models.Model):
    _name = 'setu.pharma.ex.headquarter'

    headquarter_id = fields.Many2one('setu.pharma.headquarters')
    city_id = fields.Many2one('setu.pharma.city', string="city")
    distance = fields.Float(string="Distance")

    @api.constrains('city_id')
    def unique_city(self):
        for ex_headquater in self:
            quarter = self.search([('id', '!=', ex_headquater.id), ('city_id', '=', ex_headquater.city_id.id),
                                  ('headquarter_id', '=', ex_headquater.headquarter_id.id)])
            if quarter:
                raise UserError(_('city must be unique !!!'))
