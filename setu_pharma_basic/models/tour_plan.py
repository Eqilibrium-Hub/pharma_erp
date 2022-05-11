import logging
from datetime import timedelta, datetime

from ..tools.datetime_tools import get_daterange
from odoo import fields, models, api, _

logger = logging.getLogger(__name__)


class TourPlan(models.Model):
    _name = 'setu.pharma.tour.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Tour Plan of Company"

    name = fields.Char(string='Tour Plan Reference', required=True, copy=False,
                       readonly=True,
                       index=True, default=lambda self: _('New'))
    employee_id = fields.Many2one("hr.employee", string="Employee",
                                  default=lambda self: self.env.user.employee_id)
    designation_id = fields.Many2one("setu.pharma.designation", string="Designation",
                                     default=lambda self: self.env.user.employee_id.designation_id)
    date = fields.Date(string="Tour date", default=fields.Date.today())
    state = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ],
        compute="_compute_state", string="Status", depends=['approval_request_id.request_status'],
        copy=False, store=True, default='new',
        help="Approving status")
    requester_id = fields.Many2one("res.users", string="Requester",
                                   default=lambda self: self.env.user)
    approval_request_id = fields.Many2one('approval.request', "Approval Request")
    division_id = fields.Many2one("setu.pharma.division", string="Division", copy=False,
                                  default=lambda self: self.env.user.employee_id.division_id)
    period_id = fields.Many2one("setu.pharma.fiscalperiod", string="Fiscal period")
    company_id = fields.Many2one("res.company", string="Company",
                                 default=lambda self: self.env.company, required=True)
    tour_plan_lines = fields.One2many('setu.pharma.tour.plan.line', 'tour_id', 'Tour Plan Lines')
    total_of_planned_date = fields.Integer('Total Plans', compute="_compute_total_plans")

    @api.depends('tour_plan_lines')
    def _compute_total_plans(self):
        """ Compute total calls. """
        for tp in self:
            tp.total_of_planned_date = len(tp.tour_plan_lines)

    def generate_tour_plan_lines(self):
        for tp in self:
            tp_line_vals = []
            for date in get_daterange(self.period_id.start_date, self.period_id.end_date):
                tp_line_vals.append(
                    (0, 0, {
                        'working_date_start': date,
                    }
                     )
                )
            tp.tour_plan_lines = tp_line_vals

    def _compute_state(self):
        for tour in self:
            tour.state = tour.approval_request_id.request_status or tour.state
            if tour.state == 'approved':
                tour.create_daily_call_reports()

    def create_daily_call_reports(self):
        for tour in self:
            tour.create_dcr_records()
        return True

    def create_dcr_records(self):
        logger = logging.getLogger(__name__ + "create_dcr_records")
        working_date, end_date = self.tour_plan_lines[0].working_date_start, \
                                 self.tour_plan_lines[-1].working_date_start
        date_range = get_daterange(working_date, end_date)
        for date_to_create_dcr in date_range:
            dcr_id = self.env['setu.pharma.employee.daily.call'].create(
                {'division_id': self.division_id.id,
                 'employee_id': self.employee_id.id,
                 'headquarter_id': self.employee_id.headquarter_id.id,
                 'call_date': date_to_create_dcr,
                 'tour_plan_id': self.id,
                 })
            logger.info("DCR: {dcr_set} , Created For Tour Plan: {tp_set}".format(
                tp_set=(self, self.name), dcr_set=(dcr_id, dcr_id.name)))

    @api.model
    def create(self, vals_list):
        """
        Functionality:
            - Create New Record Name Based on the sequence.
        """
        if vals_list.get('name', _('New')) == _('New'):
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'setu.pharma.tour.plan.seq') or _('New')
        tour_plan = super(TourPlan, self).create(vals_list)
        return tour_plan

    def action_open_tour_plan_calendar(self):
        tp_line_action = self.env.ref('setu_pharma_basic.action_tour_plan_line').read()[0]
        tp_line_action['domain'] = [
            ('tour_id', '=', self.id),
        ]
        tp_line_action['context'] = {
            'default_tour_id': self.id,
            'default_mode': 'month',
            'initial_date': self.period_id.start_date,
        }
        return tp_line_action

    def click_on_submitted(self):
        for tour_plan in self:
            if tour_plan:
                approval_category = self.env.ref(
                    'setu_pharma_basic.approval_category_data_tour_plan_approval')
                self.env['setu.pharma.area'].create_approval_request_and_confirm(approval_category,
                                                                                 model_record=tour_plan)
