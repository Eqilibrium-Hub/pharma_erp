from odoo import models, fields, api


class EmployeeDailyCallReportLineForDoctors(models.Model):
    _inherit = 'setu.pharma.employee.daily.call.line'

    is_return_trip = fields.Boolean(string="Return Trip ?")

    def get_configurator(self, expense_type_id):
        rec = self.env["hr.expense.configurator"].search(
            [('designation_ids', 'in', self.dcr_id.employee_id.designation_id.id),
             ('expense_type_id', '=', expense_type_id.id)], limit=1, order='id desc')
        return rec

    def create_expense_rec(self, name, expense_qty, price):
        self.env['hr.expense'].create({
            'name': name,
            'unit_amount': price,
            'product_id': self.env["product.product"].search([('can_be_expensed', '=', True)], limit=1).id,
            'quantity': expense_qty,
            'employee_id': self.dcr_id.employee_id.id,
            'dcr_history_id': self.dcr_id.id
        })

    def prepare_description(self, entry, expense, is_revers=False):
        description = self.dcr_id.headquarter_id.name + ' To ' + self.city_id.name
        if entry % 2 == 0 or is_revers:
            description = self.city_id.name + ' To ' + self.dcr_id.headquarter_id.name
        return '{} ({}) - {}'.format(self.work_type.name, description, expense.name)

    def get_rate_based_on_distance(self, configurator, unit):
        distance_lines = configurator.distance_range_ids.filtered(lambda line: line.distance_range > unit and self.dcr_id.employee_id.designation_id.id in line.designation_ids.ids)
        return distance_lines[0].amount if distance_lines else 0
