from lxml import etree
import json as simplejson
from dateutil.relativedelta import relativedelta
from odoo import fields, models, _, api


class EmployeeDailyCallReport(models.Model):
    _name = 'setu.pharma.employee.daily.call'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Daily Call Report for the Employees"
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
    distance_calculation_type = fields.Selection([
        ('max_km', 'Maximum Kilometers'),
        ('separate_km', 'Separate Kilometers'),
    ], string='Distance Calculation')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    ], default='draft', string='State')
    is_join_working = fields.Boolean("Is Join Working?")
    total_of_call_history = fields.Integer('Total Calls', compute="_compute_total_calls")

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
        return super(EmployeeDailyCallReport, self).create(vals_list)

    def action_submit_dcr(self):
        """ Submit DCR. """
        for dcr in self:
            dcr.update({'state': 'submitted'})

    def action_reset_dcr(self):
        """ Reset DCR to Draft State. """
        for dcr in self:
            dcr.update({'state': 'draft'})

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                      submenu=submenu)
        doc = etree.fromstring(res['arch'])
        if view_type == 'form':
            try:
                active_id = self._context['params']['id']
            except:
                return res
            active_id_browsable = self.env['setu.pharma.employee.daily.call'].browse(active_id)
            call_date = active_id_browsable.call_date

            # Code For Lock DCR for Edit based on Employee's DCR Edit Lock Days Also If
            # Submited Than Also Readonly
            dcr_edit_days = active_id_browsable.employee_id.dcr_edit_lock_days
            call_date_edit = call_date + relativedelta(days=+ dcr_edit_days)
            remaining_day_for_edit = (call_date_edit - fields.Date.today()).days
            if remaining_day_for_edit < 1 or active_id_browsable.state == 'submitted':
                for node in doc.xpath("//field"):
                    modifiers = simplejson.loads(node.get("modifiers"))
                    modifiers['readonly'] = True
                    node.set('modifiers', simplejson.dumps(modifiers))

            """Code For Lock DCR for Submit based on Employee's DCR Submit Lock Days"""
            dcr_submit_days = active_id_browsable.employee_id.dcr_submit_lock_days
            call_date_submit = call_date + relativedelta(days=+ dcr_submit_days)
            remaining_day_for_submit = (call_date_submit - fields.Date.today()).days
            if remaining_day_for_submit < 1:
                active_id_browsable.state = 'submitted'
            else:
                active_id_browsable.state = 'draft'

        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
