# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from ..tools.datetime_tools import get_list_of_months as months


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mandatory_select_doctors = fields.Boolean("Mandatory Select Doctors",
                                              help="Mark to add doctors mandatory while creating "
                                                   "Tour Plan")
    raise_validation_tp = fields.Boolean("Raise Validation While Creating Tour Plan",
                                         help="Mark to add doctors mandatory while creating "
                                              "Tour Plan")
    create_dcr_on_tp_approval = fields.Boolean("Create Daily Call Report On Tour Plan Approval",
                                               help="Mark to create daily call report on tour "
                                                    "plan approval")
    days = fields.Integer(string="Enter Number of Days", default=5)
    choice = fields.Selection([
        ('last', 'Last')
    ], string="Select Last Days Of Month Or First Days Of Month",
        help="Select Last Days Of Month Or First Days Of Month", default='last'
    )
    start_month = fields.Selection(string="Start Month", selection=months())
    end_month = fields.Selection(string="End Month", selection=months(), store=True, compute="_compute_start_month")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('setu_pharma_basic.mandatory_select_doctors',
                                                  self.mandatory_select_doctors)
        self.env['ir.config_parameter'].set_param('setu_pharma_basic.raise_validation_tp',
                                                  self.raise_validation_tp)
        self.env['ir.config_parameter'].set_param('setu_pharma_basic.days', self.days)
        self.env['ir.config_parameter'].set_param('setu_pharma_basic.choice', self.choice)
        self.env['ir.config_parameter'].set_param('setu_pharma_basic.create_dcr_on_tp_approval',
                                                  self.create_dcr_on_tp_approval)
        self.env['ir.config_parameter'].set_param('setu_pharma_basic.start_month', self.start_month)
        self.env['ir.config_parameter'].set_param('setu_pharma_basic.end_month',
                                                  self.end_month)

        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        mandatory_select_doctors = ICPSudo.get_param('setu_pharma_basic.mandatory_select_doctors')
        raise_validation_tp = ICPSudo.get_param('setu_pharma_basic.raise_validation_tp')
        days = ICPSudo.get_param('setu_pharma_basic.days')
        choice = ICPSudo.get_param('setu_pharma_basic.choice')
        create_dcr_on_tp_approval = ICPSudo.get_param('setu_pharma_basic.create_dcr_on_tp_approval')
        start_month = ICPSudo.get_param('setu_pharma_basic.start_month')
        end_month = ICPSudo.get_param('setu_pharma_basic.end_month')
        res.update(
            mandatory_select_doctors=mandatory_select_doctors,
            raise_validation_tp=raise_validation_tp,
            days=days,
            choice=choice,
            create_dcr_on_tp_approval=create_dcr_on_tp_approval,
            start_month=start_month,
            end_month=end_month

        )
        return res

    @api.onchange('mandatory_select_doctors')
    def onchange_mandatory_select_doctors(self):
        for record in self:
            if record.mandatory_select_doctors == False:
                record.raise_validation_tp = False

    @api.constrains('days')
    def _constrains_max_input_days_domain(self):
        for rec in self:
            if rec.days and rec.choice and (rec.days < 1 or rec.days > 31):
                raise ValidationError(_("Select Days Between 1 to 31 Only."))

    @api.onchange('start_month')
    @api.depends('start_month')
    def _compute_start_month(self):
        for fy in self:
            if fy.start_month in ['0', False, None]:
                fy.end_month = False
            else:
                fy.end_month = '12' if fy.start_month == '1' else str(
                    int(fy.start_month) - 1)