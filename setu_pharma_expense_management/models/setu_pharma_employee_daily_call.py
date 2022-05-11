from odoo import fields, models, _, api


class EmployeeDailyCallReport(models.Model):
    _inherit = 'setu.pharma.employee.daily.call'

    def generate_dcr_expense(self):
        single_entry_types = []
        for dcr in self:
            rec = self.env['hr.expense'].search([('dcr_history_id', '=', dcr.id)])
            rec.unlink()
            max_record_line = dcr.daily_call_history.sorted('distance')[
                -1] if dcr.distance_calculation_type == 'max_km' else self.env['setu.pharma.employee.daily.call.line']
            max_expense_types = max_record_line.work_type.expense_type_ids.ids
            for history in dcr.daily_call_history:
                work_type = history.work_type
                for expense in work_type.expense_type_ids:
                    configurator = history.get_configurator(expense)
                    if (
                            max_record_line and expense.id in max_expense_types and history.id != max_record_line.id) or not configurator:
                        continue
                    unit = 1
                    if configurator.calculation_type == 'distance':
                        unit = max_record_line.distance if max_record_line and work_type != False else history.distance
                    price = configurator.fixed_amount if configurator.calculation_type != 'distance' else history.get_rate_based_on_distance(
                        configurator=configurator, unit=unit)
                    counts = 2 if work_type.is_two_way_entry and expense.is_two_way_entry else 1
                    for entry in range(counts):
                        name = history.prepare_description(entry + 1, expense, history.is_return_trip)
                        if expense.id in single_entry_types:
                            continue
                        history.create_expense_rec(name=name, expense_qty=unit, price=price)
                        if expense.single_entry_per_day:
                            single_entry_types.append(expense.id)