import calendar
import datetime
import os
from datetime import datetime

from dateutil import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from ..tools.datetime_tools import get_list_of_months as months


def _prepare_years():
    return [(str(i), str(i)) for i in range(1999, 2101)]


class FiscalYear(models.Model):
    _name = 'setu.pharma.fiscalyear'
    _description = "Fiscal year"

    name = fields.Char(string="Name")
    start_year = fields.Selection(string="Start Year", selection=_prepare_years())
    end_year = fields.Selection(string="End Year", selection=_prepare_years(),
                                compute="_compute_start_year", store=True)
    start_month = fields.Selection(string="Start Month", selection=months(), default="4")
    end_month = fields.Selection(string="End Month", selection=months(),
                                 compute="_compute_start_month", store=True)
    period_ids = fields.One2many("setu.pharma.fiscalperiod", "fiscalyear_id", string="Periods")

    def generate_fiscal_period(self):
        """ Prepare Dynamically Fiscal Period for 1 Year. """
        for fy in self:
            diff = relativedelta.relativedelta(
                datetime.strptime('%s-%s-%s' % (fy.end_year, fy.end_month,
                                                calendar.monthrange(int(fy.end_year),
                                                                    int(fy.end_month))[1]),
                                  '%Y-%m-%d'),
                datetime.strptime('%s-%s-01' % (fy.start_year, fy.start_month),
                                  '%Y-%m-%d')
            )
            fiscal_period_vals = []
            total_months = (diff.months + diff.years * 12) + 1
            year_month_list = fy._prepare_year_month_list(total_months)
            for year, month in year_month_list:
                last_date = calendar.monthrange(int(year), int(month))
                period_name = list(filter(lambda m: m[0] == month, months()))[0]
                fiscal_period_vals.append(
                    (0, 0, {'name': period_name[1],
                            'start_date': datetime.strptime(
                                "{}-{}-{}".format(year, month, '1'), '%Y-%m-%d'),
                            'end_date': datetime.strptime(
                                "{}-{}-{}".format(year, month, str(last_date[1])),
                                '%Y-%m-%d'),
                            'fiscalyear_id': self.id,
                            'month_name': period_name[0]
                            }
                     )
                )

            fy.period_ids = fiscal_period_vals

    def reset_fiscal_period(self):
        for fy in self:
            fy.period_ids.unlink()

    def _prepare_year_month_list(self, total_months):
        year_month_list = []
        for start_month in range(int(self.start_month), total_months + 1):
            year_month_list.append(
                (self.start_year, (list(filter(lambda m: m[0] == str(start_month),
                                               months()))[0][0])))
        if self.start_month == '1':
            return year_month_list
        for end_month in range(1, (int(self.end_month) + 1)):
            year_month_list.append((self.end_year, (list(filter(lambda m: m[0] == str(end_month),
                                                                months())))[0][0]))
        return year_month_list

    @api.onchange('start_year')
    def _onchange_start_year(self):
        if not self.start_year:
            self.end_month = False
            self.start_month = False
            self.end_year = False

    @api.constrains('end_year', 'start_year')
    def _check_valid_year(self):
        for fy in self:
            if not fy.start_year:
                fy.end_year = False
            if fy.end_year < fy.start_year:
                raise ValidationError(_("End Year must be greater than End Year."))

    @api.constrains('end_year', 'start_year')
    def _check_unique_fy_record(self):
        for fy in self:
            if fy.search(
                    [
                        ('start_year', '=', fy.start_year),
                        ('end_year', '=', fy.end_year),
                        ('id', '!=', fy.id)
                    ]
            ):
                raise ValidationError(_("Same Fiscal Year found!"))

    @api.onchange('end_year', 'start_year')
    def _onchange_name(self):
        for fiscal_rec in self:
            if fiscal_rec.start_year and fiscal_rec.end_year:
                fiscal_rec.name = "{} - {}".format(fiscal_rec.start_year,
                                                   fiscal_rec.end_year)

    @api.onchange('start_year', 'start_month')
    @api.depends('start_year', 'start_month')
    def _compute_start_year(self):
        for fy in self:
            if not fy.start_year:
                fy.end_year = False
            else:
                fy.end_year = fy.start_year if fy.start_month == '1' and fy.end_month == '12' \
                    else str(int(fy.start_year) + 1)
                if fy.start_year == '1999' and fy.end_year == '1999' and fy.start_month == '1':
                    fy.start_month = '1'
                else:
                    fy.start_month = fy.start_month

    @api.onchange('start_month')
    @api.depends('start_month')
    def _compute_start_month(self):
        for fy in self:
            if fy.start_month in ['0', False, None]:
                fy.end_month = False
            else:
                fy.end_month = '12' if fy.start_month == '1' else str(
                    int(fy.start_month) - 1)
