from odoo import fields, models, api, _
import datetime
from ..tools.datetime_tools import *
import calendar
import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

day_names = [(str(i), calendar.day_name[i]) for i in range(0, 7)]


class TourPlanLine(models.Model):
    _name = 'setu.pharma.tour.plan.line'
    _description = "Pharma Tour Plan Line"
    _rec_name = 'tour_id'

    tour_id = fields.Many2one('setu.pharma.tour.plan', 'Tour Plan', ondelete="cascade")
    city_id = fields.Many2one('res.city', 'City')
    working_date_start = fields.Datetime('Start Time')
    working_date_end = fields.Datetime('End Time')
    dcr_id = fields.Many2one('setu.pharma.employee.daily.call', 'DCR Reference')
    day_name = fields.Selection(selection=get_list_of_day_name(), string='Day',
                                compute="_compute_working_date_start")
    visiting_partner_ids = fields.Many2many('res.partner',
                                            'res_partner_tour_plan_line_rel',
                                            'tp_line_id', 'partner_id',
                                            'Doctors/Stockists/Chemists')
    day_working_type = fields.Many2one('setu.pharma.work.type', 'Working Type',
                                       default=lambda self: self.env.ref(
                                           'setu_pharma_basic.setu_pharma_work_type_RW',
                                           raise_if_not_found=False))
    visit_counts = fields.Integer('Planned Call', compute='_count_total_visits', store=True)

    ex_headquarter_id = fields.Many2one('setu.pharma.ex.headquarter', string='City')
    headquarter_id = fields.Many2one(related='tour_id.headquarter_id', string="Headquarter")
    state = fields.Selection(related='tour_id.state')

    @api.depends('visiting_partner_ids')
    def _count_total_visits(self):
        for tp_line in self:
            tp_line.visit_counts = len(tp_line.visiting_partner_ids)

    def name_get(self):
        """ Tour Line Name Preparation """
        tour_line_names = []
        for line in self:
            state = line.ex_headquarter_id and " %s" % line.ex_headquarter_id.display_name or ''
            tour_line_names.append((line.id, "%s" % state))
        return tour_line_names

    @api.onchange('working_date_start')
    @api.depends('working_date_start')
    def _compute_working_date_start(self):
        for tp_line in self:
            tp_line.day_name = tp_line.working_date_start and str(
                tp_line.working_date_start.weekday()) or False
            tp_line.working_date_end = tp_line.working_date_start

    def add_partners_to_visit(self):
        if not self.ex_headquarter_id and not self.day_name == '6':
            raise ValidationError(_("Please Select the City to Visit for Date : '{date}' for "
                                    "Working Type "
                                    "'{type}'".format(date=self.working_date_end,
                                                      type=self.day_working_type.name)))
        wiz_obj = self.env['tp.line.partner.selection.wizard']
        wiz_obj = wiz_obj.create({
            'tp_line': self.id,
            'city_id': self.ex_headquarter_id.city_id.id,
            'partner_ids': [(6, 0, self.visiting_partner_ids.ids)]

        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Doctor/Stockists/Chemists Selection Wizard'),
            'res_model': 'tp.line.partner.selection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': wiz_obj.id,
            'context': {'active_id': wiz_obj.id},
            'views': [[False, 'form']]
        }

    @api.model
    def create(self, vals):
        ctx = self.env.context
        if ctx.get('default_tour_id'):
            tour_id = ctx.get('default_tour_id')
        else:
            tour_id = self.tour_id.search([
                ('date', '=', datetime.date.today()),('state', '!=', 'cancel')]
                , limit=1).id
        if 'tour_id' not in vals:
            vals.update({'tour_id': tour_id})
        return super(TourPlanLine, self).create(vals)

    @api.onchange('working_date_start')
    def onchange_date(self):
        """
        in this method you cant only able to select date between current fiscal period
        """
        for record in self:
            if self.tour_id.period_id.month_name != str(fields.Date.today().month):
                date = fields.Date.today() + relativedelta(months=1)
                last_date = datetime.datetime(date.year, date.month, calendar.mdays[date.month]).date()
                start_date = last_date.replace(day=1)
                if record.working_date_start != False:
                    if record.working_date_start.date() < start_date or record.working_date_start.date() > last_date:
                        raise ValidationError(_(f"You can only make plan between {start_date} to {last_date}"))
            else:
                date = fields.Date.today()
                last_date = datetime.datetime(date.year, date.month, calendar.mdays[date.month]).date()
                start_date = date
                if record.working_date_start != False:
                    if record.working_date_start.date() < start_date or record.working_date_start.date() > last_date:
                        raise ValidationError(_(f"You can only make plan between {start_date} to {last_date}"))
