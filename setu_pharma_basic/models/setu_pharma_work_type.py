from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PharmaWorkType(models.Model):
    _name = 'setu.pharma.work.type'
    _description = 'Pharma Work Type'

    name = fields.Char("Name")
    code = fields.Char("Code")
    applicable_for_allowance = fields.Boolean("Allowance Applicable?")

    def name_get(self):
        """ Work Type Name Preparation """
        types = []
        for w_type in self:
            types.append((w_type.id, "%s - %s" % (w_type.name, w_type.code)))
        return types

    @api.constrains('code')
    def _check_work_type_code(self):
        """ Check constrains for same Work Type Code. """
        for work_type in self:
            if self.with_context(active_test=False).search([
                ('code', '=ilike', work_type.code),
                ('id', '!=', work_type.id),
            ]):
                raise ValidationError(_("Duplicate Work Type Code Found.\nPlease Add Different "
                                        "Code."))
