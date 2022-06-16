from collections import defaultdict
from datetime import datetime,date
from dateutil import relativedelta
from werkzeug.urls import url_encode
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from ..tools.datetime_tools import get_daterange
import calendar
import datetime
import logging

logger = logging.getLogger(__name__)


class TourPlan(models.Model):
    _name = 'setu.pharma.tour.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Pharma Tour Plan"

    def current_next_fiscal_period(self):
        period = self.env['setu.pharma.fiscalyear'].search(
            [('start_year', '=', datetime.datetime.now().year)], order='end_month desc').period_ids.filtered(
            lambda year: year.name == datetime.datetime.now().strftime('%B') or year.name == (
                    datetime.datetime.now() + relativedelta.relativedelta(months=1)).strftime('%B')).mapped('id')
        domain = [('id', 'in', period)]
        return domain

    name = fields.Char(string='Tour Plan Reference', required=True, copy=False,
                       readonly=True,
                       index=True, default=lambda self: _('New'))
    employee_id = fields.Many2one("hr.employee", string="Employee",
                                  default=lambda self: self.env.user.employee_id)
    designation_id = fields.Many2one("setu.pharma.designation", string="Designation",
                                     default=lambda self: self.env.user.employee_id.designation_id)
    date = fields.Date(string="Tour date", default=fields.Date.today(), readonly=True)
    state = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancelled'),
    ],
        compute="_compute_state", string="Status", depends=['approval_request_id.request_status'],
        copy=False, store=True, default='new',
        help="Approving status")
    requester_id = fields.Many2one("res.users", string="Requester",
                                   default=lambda self: self.env.user)
    approval_request_id = fields.Many2one('approval.request', "Approval Request",
                                          ondelete='cascade')
    division_id = fields.Many2one("setu.pharma.division", string="Division", copy=False,
                                  default=lambda self: self.env.user.employee_id.division_id)
    period_id = fields.Many2one("setu.pharma.fiscalperiod", string="Fiscal period", domain=current_next_fiscal_period,
                                compute="_compute_fiscal_period", store=True)
    company_id = fields.Many2one("res.company", string="Company",
                                 default=lambda self: self.env.company, required=True)
    tour_plan_lines = fields.One2many('setu.pharma.tour.plan.line', 'tour_id', 'Tour Plan Lines')
    total_of_planned_date = fields.Integer('Total Plans', compute="_compute_total_plans")
    headquarter_id = fields.Many2one(related='employee_id.headquarter_id', string="Headquarter")
    parent_id = fields.Many2one(related='employee_id.parent_id', string="Manager")
    tp_line_generated = fields.Boolean('Is TP Line Generated?')

    @api.depends('tour_plan_lines')
    def _compute_total_plans(self):
        """ Compute total calls. """
        for tp in self:
            tp.total_of_planned_date = len(tp.tour_plan_lines)

    def generate_tour_plan_lines(self):
        for tp in self:
            tp_line_vals = []
            if self.period_id.month_name != str(fields.Date.today().month):
                for date in get_daterange(self.period_id.start_date, self.period_id.end_date):
                    tp_line_vals.append(
                        (0, 0, {
                            'working_date_start': date,
                        }
                         )
                    )
            else:
                for date in get_daterange(fields.Date.today(), self.period_id.end_date):
                    tp_line_vals.append(
                        (0, 0, {
                            'working_date_start': date,
                        }
                         )
                    )
            tp.tour_plan_lines = tp_line_vals
            tp.tp_line_generated = True

    def _compute_state(self):
        for tour in self:
            tour.state = tour.approval_request_id.request_status or tour.state
            dcr_config = self.env['ir.config_parameter'].sudo().get_param(
                'setu_pharma_basic.create_dcr_on_tp_approval')
            if tour.state == 'approved' and dcr_config:
                tour.create_daily_call_reports()
            if tour.state == 'new':
                tour.tour_plan_lines = [(6, 0, False)]
                tour.tp_line_generated = False

    @api.model
    def default_get(self, fields):
        result = super(TourPlan, self).default_get(fields)
        default = self.env['setu.pharma.fiscalperiod'].search(
            [('start_date', '<=', date.today()),
             ('end_date', '>=', date.today())
             ], limit=1)
        if default:
            result.update({'period_id': default.id + 1})
        else:
            result.update({'period_id': 0})
        return result

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

    def write(self, vals):
        result = super(TourPlan, self).write(vals)
        for tp in self:
            if not tp.period_id:
                raise ValidationError("Please Select Fiscal Period.")
        return result

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
        if not tour_plan.period_id:
            raise ValidationError("Please Select Fiscal Period.")
        days = int(self.env['ir.config_parameter'].sudo().get_param('setu_pharma_basic.days'))
        date = fields.Date.today()
        """
        This method give error if current date is not between start and last date to create tourplan
        """
        if tour_plan.period_id.month_name != str(date.month):
            """Last Date Of Month Or Last Date To Create To Plan"""
            ldofmonth = datetime.datetime(date.year, date.month, calendar.mdays[date.month]).date()
            """Start Date For Tour Plan Create"""
            start_date = ldofmonth - datetime.timedelta(days=days)
            if date < start_date:
                raise ValidationError(
                    _(f"You can only create tour plan between {start_date} to {ldofmonth}"))
        """
        This code make tp_line_generated true on create method
        """
        if tour_plan.tour_plan_lines:
            tour_plan.tp_line_generated = True
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
        """
        Check If Tour Plan Is Zero Than Raise Error
        """
        for tp in self:
            if not tp.tour_plan_lines:
                raise ValidationError(_("Tourplan line is mandatory Generate or Add TP line"))
            if tp.tour_plan_lines.filtered(lambda x: not x.ex_headquarter_id and x.day_name != '6'):
                raise ValidationError(_("Tour Plan Line City Adding is mandatory."))
            if tp.period_id.id == False:
                raise ValidationError(
                    _("Fiscal period not found please go to configuration/fiscal year and "
                      "create fiscal year and generate fiscal period"))

            if tp.env['ir.config_parameter'].sudo().get_param(
                    'setu_pharma_basic.mandatory_select_doctors'):
                for tp in tp.tour_plan_lines:
                    if tp.visit_counts < 1:
                        raise ValidationError(_("Doctor selection is mandatory"))

                if tp.env['ir.config_parameter'].sudo().get_param(
                        'setu_pharma_basic.raise_validation_tp'):
                    doctorsdict = defaultdict()
                    empdoctor = set()
                    for tp in tp.tour_plan_lines:
                        for doctor in tp.visiting_partner_ids:
                            if doctor.name in doctorsdict.keys():
                                count = doctorsdict[doctor.name][1] + 1
                                doctorsdict[doctor.name][1] = count
                            else:
                                doctorsdict[doctor.name] = [doctor.total_visit, 1]
                    for doctor in tp.employee_id.doctor_ids:
                        empdoctor.add(doctor.partner_id.name)
                    for [total_visit, vc_per_doctor] in doctorsdict.values():
                        if set(doctorsdict.keys()) == empdoctor:
                            if total_visit > vc_per_doctor:
                                raise ValidationError(
                                    _("Total visit of doctors are not fulfilled."))
                        else:
                            raise ValidationError(_("Total visit of doctors are not fulfilled."))
            approval_category = self.env.ref(
                'setu_pharma_basic.approval_category_data_tour_plan_approval')
            self.env['setu.pharma.area'].create_approval_request_and_confirm(approval_category,
                                                                             model_record=tp)

            url = '/web#%s' % url_encode({
                'action': 'approvals.approval_request_action_to_review',
                'active_id': tp.approval_request_id.id,
                'active_model': 'setu.pharma.tour.plan',
                'menu_id': self.env.ref('approvals.approvals_menu_root').id,
            })
            if tp.date != datetime.date.today():
                tp.date = datetime.date.today()
            tp._message_log(body=_('<b>Tour Plan Submitted Successfully!</b> '
                                   'You can review your Approval Request '
                                   '<a href="%s">%s</a>') % (url, tp.approval_request_id.name))

        if len(self) == 1:
            """ Return Rainbow effect on tp submit """
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Tour plan submitted successfully',
                    'type': 'rainbow_man',
                }
            }

    def action_reset_tp(self):
        """ Reset Tour Plan with its associated approval request. """
        for record in self:
            record.approval_request_id.action_draft()
            record.tour_plan_lines.unlink()
            record.tp_line_generated = False

    @api.onchange('tour_plan_lines')
    def onchange_tour_plan_lines(self):
        """ Update TP Line Generated Boolean. """
        for tp in self:
            if tp.tour_plan_lines:
                tp.tp_line_generated = True
            else:
                tp.tp_line_generated = False

    @api.constrains('period_id')
    def _check_fiscal_period_tp_plan(self):
        """This method generate error if we create multiple tour plan on same fiscal year"""
        for tp in self:
            if tp.search([('period_id', '=', tp.period_id.id), ('id', '!=', tp.id),
                          ('state', '!=', 'cancel')]):
                raise ValidationError(
                    _("You can't create multiple tourplan for same fiscal period"))

    def unlink(self):
        """ Unlink Inherited. """
        if self.state == 'approved':
            raise ValidationError(_("You can't delete 'Approved' Tour Plan"))
        return super(TourPlan, self).unlink()
