from odoo import models, fields, api, _
from datetime import datetime
from dateutil import relativedelta

from odoo.api import returns
from odoo.tools.populate import compute


class DoctorSupport(models.Model):
    _name = 'setu.pharma.monthly.doctor.support'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Doctor Support for Pharma Companies"

    def previous_fiscal_year(self):
        """
        Functionality:
            -To get Previous month of current month
        """
        period = self.env['setu.pharma.fiscalyear'].search(
            [('start_year', '=', datetime.now().year)]).period_ids.filtered(
            lambda year: year.name == datetime.now().strftime('%B') or year.name == (
                    datetime.now() - relativedelta.relativedelta(months=1)).strftime('%B')).mapped('id')
        domain = [('id', 'in', period)]
        return domain

    name = fields.Char(string='Doctor Support Reference', copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    fiscal_period_id = fields.Many2one("setu.pharma.fiscalperiod", string="Fiscal Period", domain=previous_fiscal_year)
    division_id = fields.Many2one("setu.pharma.division", string="Division", copy=False)
    employee_id = fields.Many2one("res.partner", string="Doctor", copy=False)
    headquarter_id = fields.Many2one('setu.pharma.headquarters', string="Headquarter")
    company_id = fields.Many2one("res.company", string="Company",
                                 default=lambda self: self.env.company)
    date = fields.Date(string="Date", copy=False, default=fields.Date.today())
    line_ids = fields.One2many("setu.pharma.monthly.doctor.support.line", "support_id",
                               string="Product Closing")
    previous_month = fields.Float(string='Previous Amount', compute="_compute_previous_month")
    total_amount = fields.Float(string='Current Amount', compute="_compute_total_amount")

    @api.model
    def default_get(self, vals):
        """
            Functionality:
                -To set default values of Doctor support
        """
        result = super(DoctorSupport, self).default_get(vals)
        fiscal_year = self.env['setu.pharma.fiscalyear'].search([('start_year', '=', datetime.now().year)])
        division = self.env['hr.employee'].search([('name', '=', self.env.user.name)])
        result.update({'employee_id': self.env.context.get('active_id'),
                       'fiscal_period_id': (
                           fiscal_year.period_ids.filtered(lambda x: x.name == datetime.now().strftime('%B'))).id,
                       'division_id': division.division_id.id,
                       'headquarter_id': division.headquarter_id.id,
                       'line_ids': [(0, 0, {'product_id': product.id}) for product in division.division_id.product_ids]
                       })
        return result

    def _compute_previous_month(self):
        """
            Functionality:
               -'Previous amount' of doctor support
        """
        self.previous_month = 0
        for data in self:
            doctor_support_line = self.env['setu.pharma.monthly.doctor.support'].search(
                [('employee_id', '=', data.employee_id.id), ('id', '<', data.id)], order='id desc', limit=1)

            if doctor_support_line:
                amount = doctor_support_line.line_ids.mapped('sub_total') or data.total_amount
                data.previous_month = sum(amount)

    @api.depends('line_ids.sub_total')
    def _compute_total_amount(self):
        for doc_sup in self:
            doc_sup.total_amount = sum(doc_sup.line_ids.mapped('sub_total')) or doc_sup.total_amount

    @api.model
    def create(self, vals_list):
        """
            Functionality:
                - Create New Record Name Based on the sequence.
        """
        if vals_list.get('name', _('New')) == _('New'):
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'setu.pharma.monthly.doctor.support.seq') or _('New')
        return super(DoctorSupport, self).create(vals_list)
