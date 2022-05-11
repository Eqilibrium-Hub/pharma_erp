from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

class City(models.Model):
    _name = 'setu.pharma.city'
    _description = "Setu Pharma City"

    # Fields Declaration
    name = fields.Char(string="City Name", copy=False)
    code = fields.Char(string="City Code", copy=False)
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country",
                                 default=lambda self: self.env.company.country_id)
    headquarter_id = fields.Many2one(comodel_name='setu.pharma.headquarters',
                                     string=' Headquarter')
    active = fields.Boolean(string="Active City", default=True, help="Currently Active City.")

    @api.constrains('code')
    def _check_city_code(self):
        """ Check constrains for same City Code. """
        for city in self:
            if self.with_context(active_test=False).search([
                ('code', '=ilike', city.code),
                ('id', '!=', city.id)
            ]):
                raise ValidationError(
                    _("Duplicate City Code Found.\nPlease Add Different City Code."))

    @api.model
    def create(self, vals):
        """ Whenever the City created, System will Update code to upper."""
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        return super(City, self).create(vals)

    def write(self, vals):
        """ Whenever the City updated, System will Update code to upper."""
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        return super(City, self).write(vals)

    def name_get(self):
        """ City Name Preparation """
        city_names = []
        for city in self:
            state = city.state_id and "- %s" % city.state_id.code or ''
            city_names.append((city.id, "%s %s" % (city.name, state)))
        return city_names

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = [
                '|','|',
                ('name', operator, name),
                ('state_id.code', operator, name),
                ('code', operator, name),
            ]
        return self._search(expression.AND([domain, args]), limit=limit,
                            access_rights_uid=name_get_uid)
