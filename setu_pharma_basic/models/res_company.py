from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    code = fields.Char(related='partner_id.code', store=True, inverse='_inverse_partner_code',
                       readonly=False)

    def _inverse_partner_code(self):
        for company in self:
            company.partner_id.code = company.code
