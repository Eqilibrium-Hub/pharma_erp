from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ExpenseType(models.Model):
    _name = 'hr.expense.type'
    _description = "For Expense type of pharma company "

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    single_entry_per_day = fields.Boolean(string="Single Entry Per Day")
    is_two_way_entry = fields.Boolean(string="Two Way Entry")

    @api.constrains('code')
    def _check_designation_name(self):
        """ Check constrains for same code in expense type"""
        for check_code in self:
            if self.with_context(active_test=False).search([
                ('code', '=ilike', check_code.code),
                ('id', '!=', check_code.id),
            ]):
                raise ValidationError(_("Expense Type Code Already Exists.\n"
                                        "Please Enter Other Code"))


