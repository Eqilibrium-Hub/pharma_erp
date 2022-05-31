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
        company_code = vals['code']
        company_create = super(ResCompany, self.with_context(default_code=company_code+"1")).create(
            vals)
        for company in company_create:
            self.env['setu.pharma.headquarters'].with_context(
                allowed_company_ids=company.ids).create({
                'name': company.name,
                'code': company.code,
                'company_id': company.id
            })
        return company_create
