from odoo import models, api, fields


class Users(models.Model):
    _inherit = 'res.users'

    code = fields.Char(related='partner_id.code', store=True, inverse='_inverse_partner_code',
                       readonly=False)

    def _inverse_partner_code(self):
        """ Inverse update Partner Code """
        for company in self:
            company.partner_id.code = company.code

    @api.model_create_multi
    def create(self, vals):
        """ Whenever the City created, System will auto create employee."""
        users = super(Users, self).create(vals)
        for user in users:
            if not user.employee_id:
                user.action_create_employee()
        return users
