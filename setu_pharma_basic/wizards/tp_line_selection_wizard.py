from odoo import fields, models, api
import calendar


class TPLinePartnersSelectionWizard(models.TransientModel):
    _name = "tp.line.partner.selection.wizard"
    _description = """Select Multiple Partners in TP Line."""

    tp_line = fields.Many2one('setu.pharma.tour.plan.line', 'TP Line')
    partner_ids = fields.Many2many('res.partner', string='Doctor/Stockist/Chemists')
    city_id = fields.Many2one('res.city', 'City')
    employee_id = fields.Many2one("hr.employee", related='tp_line.tour_id.employee_id')

    def update_tp_lines_with_selected_partners(self):
        self.tp_line.visiting_partner_ids = [
            (6, 0, self.tp_line.visiting_partner_ids.ids + self.partner_ids.ids)]
