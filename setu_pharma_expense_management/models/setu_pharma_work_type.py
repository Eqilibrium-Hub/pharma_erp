from odoo import fields, models, api, _


class PharmaWorkType(models.Model):
    _inherit = 'setu.pharma.work.type'

    expense_type_ids = fields.Many2many(comodel_name="hr.expense.type",
                                        relation="setu_pharma_work_type_expense_configurator_rel",
                                        column1="configurator_id",
                                        column2="worktype_id",
                                        string="Expense Type")
    is_two_way_entry = fields.Boolean(string="Two Way Entry")