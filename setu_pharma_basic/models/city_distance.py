from math import sin, cos, sqrt, atan2, radians
from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class CityDistance(models.Model):
    _name = 'setu.pharma.city.distance'
    _description = "City Distance"

    @api.depends('from_city_id', 'to_city_id')
    def prepare_from_to_name(self):
        for city_dist in self:
            city_dist.name = (city_dist.from_city_id.name or "") + " - " + \
                             (city_dist.to_city_id.name or "") \
                             or city_dist.name

    # Fields Declaration
    name = fields.Char(string='Name', copy=False,
                       readonly=True, compute=prepare_from_to_name,
                       index=True)
    from_city_id = fields.Many2one("res.city", string="From")
    to_city_id = fields.Many2one("res.city", string="To")
    distance = fields.Integer(string="Distance")

    @api.constrains("from_city_id", "to_city_id")
    def _check_duplicate_from_to_city(self):
        """ Check constrains for same Designation Name. """
        for record in self:
            domain = [('id', '!=', record.id), ]
            if self.search(domain + ['|', '&',
                                     ('from_city_id', '=', record.from_city_id.id),
                                     ('to_city_id', '=', record.to_city_id.id),
                                     '&',
                                     ('from_city_id', '=', record.to_city_id.id),
                                     ('to_city_id', '=', record.from_city_id.id)]):
                raise ValidationError(_("Duplicate Record Found.\n"
                                        "Please Create Different Record."))
