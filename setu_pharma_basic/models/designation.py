from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class Designation(models.Model):
    _name = 'setu.pharma.designation'
    _description = "Pharma Designations"

    # Fields Declaration
    name = fields.Char(string="Designation", copy=False)
    parent_designation = fields.Many2one('setu.pharma.designation', 'Parent Designation')
    code = fields.Char(string="Code", copy=False, size=5)
    company_id = fields.Many2one("res.company", string="Company",
                                 default=lambda self: self.env.company)
    division_ids = fields.Many2many("setu.pharma.division",
                                    'setu_pharma_designation_pharma_division_rel',
                                    'designation_id', 'division_id',
                                    string="Divisions", copy=False)
    active = fields.Boolean(string="Active Designation", default=True,
                            help="Currently Active Designation.")
    is_root_designation = fields.Boolean('Is Root Designation?',
                                         help="There is Only One Root Designation in which you "
                                              "can mark this field as True else it raise a "
                                              "Validation.")
    dcr_submit_and_edit_lock_days = fields.Integer(string="DCR Submit And Edit Lock Days", tracking=True)


    @api.constrains('code')
    def _check_designation_name(self):
        """ Check constrains for same Designation Name. """
        for designation in self:
            if self.with_context(active_test=False).search([
                ('code', '=ilike', designation.code),
                ('id', '!=', designation.id),
            ]):
                raise ValidationError(_("Duplicate Designation Code Found.\n"
                                        "Please Add Different Designation Code"))

    @api.model
    def create(self, vals):
        """ Whenever the Designation created, System will Update code to upper."""
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        return super(Designation, self).create(vals)

    def write(self, vals):
        """ Whenever the Designation updated, System will Update code to upper."""
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        return super(Designation, self).write(vals)
