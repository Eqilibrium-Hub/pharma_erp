from odoo import fields, models
from datetime import datetime
import calendar
from ..tools.datetime_tools import *


class FiscalPeriod(models.Model):
    _name = 'setu.pharma.fiscalperiod'
    _description = "Fiscal Period"

    name = fields.Char(string="Name")
    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")
    month_name = fields.Selection(string="Month", selection=get_list_of_months())
    fiscalyear_id = fields.Many2one("setu.pharma.fiscalyear", string="Fiscal year",
                                    ondelete="cascade")

    def name_get(self):
        """ Prepare Fiscal Period Name """
        fiscal_periods = []
        for fp in self:
            fy_name = fp.fiscalyear_id and "(%s)" % fp.fiscalyear_id.name or ''
            fiscal_periods.append((fp.id, "%s %s" % (fp.name, fy_name)))
        return fiscal_periods

    def get_days(self):
        return datetime.strptime(
            '{}-{}-{}'.format(datetime.now().year + 1, 2,
                              str(calendar.monthrange(datetime.now().year + 1, 2)[1])),
            '%Y-%m-%d')
