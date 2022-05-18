from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    code = fields.Char(related='partner_id.code', store=True, inverse='_inverse_partner_code',
                       readonly=False)

    def _inverse_partner_code(self):
        for company in self:
            company.partner_id.code = company.code

    @api.model
    def create(self, vals):
        """ Create New Default Headquarter. """
        company_create = super(ResCompany, self).create(vals)
        self.env['setu.pharma.headquarters'].with_context(
            allowed_company_ids=company_create.ids).create({
            'name': company_create.name,
            'code': company_create.code,
            'company_id': company_create.id
        })
        return company_create
