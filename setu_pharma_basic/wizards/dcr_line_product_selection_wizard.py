from odoo import fields, models, api
import calendar


class DCRLinePartnersSelectionWizard(models.TransientModel):
    _name = "dcr.line.product.selection.wizard"
    _description = """Select Multiple Products and quantity for DCR Line."""

    dcr_line = fields.Many2one('setu.pharma.employee.daily.call.line', 'DCR Line')
    dcr_selection_lines = fields.One2many('dcr.line.product.selection.wizard.line',
                                          'dcr_selection_wiz_id')
    partner_id = fields.Many2one('res.partner', 'Doctor')

    def update_tp_lines_with_selected_products(self):
        """ Update selected partners to dcr line"""
        product_vals = []
        for line in self.dcr_selection_lines:
            dcr_line = self.dcr_line.doctor_products.filtered(lambda x: x.id == line.product_id.id)
            if dcr_line:
                product_vals.append((0, 0, {
                    'dcr_line_id': self.dcr_line.id,
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                }))
            else:
                product_vals.append((0, 0, {
                    'dcr_line_id': self.dcr_line.id,
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                }))

        self.dcr_line.doctor_products = [(5, 0)]
        self.dcr_line.doctor_products = product_vals


class DCRLineProductSelectionWizardLines(models.TransientModel):
    _name = "dcr.line.product.selection.wizard.line"
    _description = "DCR Line Product Selection Wizard Line"

    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float('Quantity')
    dcr_selection_wiz_id = fields.Many2one('dcr.line.product.selection.wizard', 'DCR Wiz')
