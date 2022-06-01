from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError

class City(models.Model):
    _inherit = "res.city"

    code = fields.Char(string="City Code", copy=False)
    headquarter_id = fields.Many2one(comodel_name='setu.pharma.headquarters',
                                     string=' Headquarter')

    @api.constrains('name')
    def _constrains_check_bom_id(self):
        """
        Added By: Jigna J Savaniya | Date: 1st June,2022 | Task: Main
        Use: This method will not allow creating duplicate City
        """
        for rec in self:
            city_exist = self.search([('id', '!=', rec.id),
                                      ('name', '=', rec.name),
                                      ('country_id', '=', rec.country_id.id),
                                      ('state_id', '=', rec.state_id.id)])
            if city_exist:
                raise UserError(_('City should be unique !!'))

