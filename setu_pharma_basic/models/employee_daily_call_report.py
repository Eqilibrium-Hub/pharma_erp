from datetime import date
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import fields, models, _, api


class EmployeeDailyCallReport(models.Model):
    _name = 'setu.pharma.employee.daily.call'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Daily Call Report"
    _order = "name desc"

    name = fields.Char(string='Daily Call Report Reference', required=True, copy=False,
                       readonly=True,
                       index=True, default=lambda self: _('New'))
    employee_id = fields.Many2one("hr.employee", string="Employee", copy=False,
                                  default=lambda self: self.env.user.employee_id)
    division_id = fields.Many2one("setu.pharma.division", string="Division",
                                  related='employee_id.division_id',
                                  copy=False)
    headquarter_id = fields.Many2one('setu.pharma.headquarters', 'Headquarter',
                                     related='employee_id.headquarter_id')
    call_date = fields.Date(string="Call date", default=fields.Date.today())
    daily_call_history = fields.One2many('setu.pharma.employee.daily.call.line',
                                         'dcr_id')
    company_id = fields.Many2one("res.company", string="Company",
                                 default=lambda self: self.env.company)
    tour_plan_id = fields.Many2one('setu.pharma.tour.plan', 'Tour Plan')
    tour_plan_line_ids = fields.One2many(related='tour_plan_id.tour_plan_lines', string='Tour Plan Line')
    distance_calculation_type = fields.Selection([
        ('max_km', 'Maximum Kilometers'),
        ('separate_km', 'Separate Kilometers'),
    ], string='Distance Calculation')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('arsubmitted', 'Approval Request Submitted'),
        ('approved', 'Approved'),
        ('submitted', 'DCR Submitted'),
        ('refused', 'Refused'),
        ('cancel', 'Cancelled'),
    ], depends=['approval_request_id.request_status'],
        copy=False, store=True, compute="_compute_state",
        default='draft', string='State')
    is_join_working = fields.Boolean("Is Join Working?")
    total_of_call_history = fields.Integer('Total Calls', compute="_compute_total_calls")
    approval_request_id = fields.Many2one('approval.request', "Approval Request",
                                          ondelete='cascade')
    requester_id = fields.Many2one("res.users", string="Requester",
                                   default=lambda self: self.env.user)
    readonly_line = fields.Boolean(default=True)
    lock_days = fields.Boolean(default=True)

    def _compute_state(self):
        for emp_dcr in self:
            if emp_dcr.approval_request_id.request_status == 'approved':
                emp_dcr.readonly_line = False
            elif emp_dcr.approval_request_id.request_status == 'refused' or emp_dcr.approval_request_id.request_status == 'cancel' or emp_dcr.approval_request_id.request_status == 'pending':
                emp_dcr.readonly_line = True
            if emp_dcr.approval_request_id.request_status == 'pending':
                emp_dcr.state = 'arsubmitted'
            else:
                emp_dcr.state = emp_dcr.approval_request_id.request_status or emp_dcr.state

            daysdiff = date.today() - emp_dcr.call_date
            if daysdiff.days > emp_dcr.employee_id.designation_id.dcr_submit_and_edit_lock_days:
                emp_dcr.lock_days = True

    @api.depends('daily_call_history')
    def _compute_total_calls(self):
        """ Compute total calls. """
        for dcr in self:
            dcr.total_of_call_history = len(dcr.daily_call_history)

    def action_open_call_history(self):
        """ Call Calendar View for the Call History. """
        self.ensure_one()
        dcr_line_action = self.env.ref(
            'setu_pharma_basic.action_employee_daily_call_report_line').read()[0]
        dcr_line_action['view_id'] = self.env.ref(
            'setu_pharma_basic.view_employee_daily_call_report_line_tree').id
        dcr_line_action['domain'] = [('dcr_id', '=', self.id)]
        dcr_line_action['context'] = {
            'default_dcr_id': self.id,
            'default_mode': 'day',
            'initial_date': self.call_date,
        }
        return dcr_line_action

    @api.model
    def create(self, vals_list):
        """
        Functionality:
            - Create New Record Name Based on the sequence.
        """
        if vals_list.get('name', _('New')) == _('New'):
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'setu.pharma.employee.daily.call.seq') or _('New')
        """
        This method is generate approval request if dcr date before lock days
        """
        emp_dcr = super(EmployeeDailyCallReport, self).create(vals_list)
        daysdiff = date.today() - emp_dcr.call_date
        if emp_dcr and daysdiff.days > emp_dcr.employee_id.designation_id.dcr_submit_and_edit_lock_days:
            emp_dcr.readonly_line = True
            approval_category = self.env.ref(
                'setu_pharma_basic.approval_category_data_dcr_approval')
            self.env['setu.pharma.area'].create_approval_request_and_confirm(approval_category,
                                                                             model_record=emp_dcr)
        else:
            emp_dcr.readonly_line = False
        return emp_dcr

    """
    This method is generate approval request if dcr date before lock days
    """
    def write(self, vals):
        for emp_dcr in self:
            if vals.get('call_date'):
                call_date = datetime.strptime(vals.get('call_date'), '%Y-%m-%d').date()
                daysdiff = date.today() - call_date
                if emp_dcr and daysdiff.days > emp_dcr.employee_id.designation_id.dcr_submit_and_edit_lock_days:
                    vals.update({'readonly_line': True})
                    approval_category = self.env.ref(
                        'setu_pharma_basic.approval_category_data_dcr_approval')
                    self.env['setu.pharma.area'].create_approval_request_and_confirm(approval_category,
                                                                                     model_record=emp_dcr)
                else:
                    vals.update({'readonly_line': False})
        return super(EmployeeDailyCallReport, self).write(vals)

    def action_submit_dcr(self):
        """ Submit DCR. """
        for dcr in self:
            dcr.update({'state': 'submitted'})

    def action_reset_dcr(self):
        """ Reset DCR to Draft State. """
        for dcr in self:
            dcr.update({'state': 'draft'})


    @api.model
    def default_get(self, fields):
        """
            This Method get default tourplan in employee daily call report if tourplan created for this month
        """
        res = super(EmployeeDailyCallReport, self).default_get(fields)
        working_date = datetime.combine(date.today() + relativedelta(months=1), datetime.min.time())
        tourplan = self.env['setu.pharma.tour.plan.line'].search([('working_date_start', '=', working_date)]).tour_id.id
        res.update({'tour_plan_id': tourplan})
        return res
