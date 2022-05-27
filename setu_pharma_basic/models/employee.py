from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from collections import defaultdict


class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    area_ids = fields.Many2many("setu.pharma.area",
                                'setu_pharma_area_hr_employee_rel',
                                'employee_id',
                                'pharma_area_id',
                                string="Areas", copy=False)
    division_id = fields.Many2one("setu.pharma.division", string="Division",
                                  copy=False)
    designation_id = fields.Many2one("setu.pharma.designation", string="Designation",
                                     copy=False)
    dcr_submit_lock_days = fields.Integer(string="DCR Submit Lock Days", tracking=True)
    dcr_edit_lock_days = fields.Integer(string="DCR Edit Lock Days", tracking=True)
    aadhar_no = fields.Char(string="Aadhar No", size=12, copy=False)
    pan_no = fields.Char(string="PAN No", size=10, copy=False)
    headquarter_id = fields.Many2one(comodel_name="setu.pharma.headquarters", string="Headquarter",
                                     copy=False)
    stock_location_id = fields.Many2one('stock.location', 'Employee Stock Location')
    doctor_ids = fields.One2many('hr.employee.line', 'employee_id')
    job_ex_num = fields.Integer('Job Experience')
    job_ex_num_ymd = fields.Selection([('day', 'Day'), ('month', 'Month'), ('year', 'Year')])
    departure_reason = fields.Char(related='departure_reason_id.name')

    @api.constrains('pan_no')
    def _check_pan_no(self):
        """ Check constrains for same PAN No. """
        for employee in self:
            if self.with_context(active_test=False).search([
                ('pan_no', '=ilike', employee.pan_no),
                ('id', '!=', employee.id),
            ]):
                raise ValidationError(_("Duplicate PAN No Found.\nPlease Add Different PAN No"))

    @api.constrains('aadhar_no')
    def _check_aadhar_no(self):
        """ Check constrains for same Aadhar No. """
        for employee in self:
            if self.with_context(active_test=False).search([
                ('aadhar_no', '=ilike', employee.aadhar_no),
                ('id', '!=', employee.id),
            ]):
                raise ValidationError(_("Duplicate Aadhar No. Found.\n"
                                        "Please Add Different Aadhar No."))


class HrEmployeeLine(models.Model):
    _name = 'hr.employee.line'
    _description = "HR Employee Line"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    partner_id = fields.Many2one('res.partner', 'Doctor', domain=[('is_doctor', '=', True)],
                                 required=True)
    dr_degree = fields.Many2many(related='partner_id.degree_tag_ids',
                                 relation='emp_line_dr_degree_rel',
                                 column1='emp_line_id', column2='degree_id',
                                 string='Degrees')
    dr_class = fields.Many2one(related='partner_id.doctor_class',
                               string='Class')
    total_visit = fields.Integer('Total Visit', default=1)
    headquarter_city = fields.Many2one(related='employee_id.headquarter_id.city_id',
                                       string='HQ City')
    dr_city = fields.Char(related='partner_id.city', string='City')

    @api.constrains('partner_id')
    def _check_exist_partner_id(self):
        for partner in self:
            exist_product_list = []
            for line in partner.employee_id.doctor_ids:
                if line.partner_id.id in exist_product_list:
                    raise ValidationError(_('Doctor should be one per line.'))
                exist_product_list.append(line.partner_id.id)
