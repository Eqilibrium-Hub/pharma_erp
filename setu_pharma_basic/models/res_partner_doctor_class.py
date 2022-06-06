from odoo import fields, models, api
from random import randint

class ResPartnerDoctorClass(models.Model):
    _name = 'res.partner.doctor.class'
    _description = 'Doctor Class'

    def _get_default_color(self):
        """ Default Color for Doctor Class. """
        return randint(1, 11)

    name = fields.Char(string='Class Name', required=True, translate=True)
    color = fields.Integer(string='Color', default=_get_default_color)
