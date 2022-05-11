from odoo import models, fields, api
import datetime


class EmployeeDailyCallReportLine(models.Model):
    _name = 'setu.pharma.employee.daily.call.line'
    _description = "Daily Call Report line for the Employees to Doctors"
    _rec_name = 'dcr_id'

    @api.model
    def default_get(self, field_list):
        """ Add Default DCR for Call History when the Page was reloaded or directly opened the
        DCR View. """
        search_and_add_dcr_id = False
        if 'dcr_id' not in field_list:
            field_list += ['dcr_id']
            search_and_add_dcr_id = True
        defaults = super(EmployeeDailyCallReportLine, self).default_get(field_list)
        if search_and_add_dcr_id:
            defaults.update({
                'dcr_id': self.dcr_id.search([('call_date', '=', datetime.date.today())], limit=1)
            })
        return defaults

    dcr_id = fields.Many2one('setu.pharma.employee.daily.call', 'DCR Reference')
    call_date = fields.Date(related='dcr_id.call_date', string='Call Date', store=True)
    call_date_start = fields.Datetime('Call Start')
    call_date_end = fields.Datetime('Call End')
    manager_ids = fields.Many2many("hr.employee",
                                   'setu_pharma_hr_employee_daily_call_line_doctors_report_rel',
                                   'employee_id',
                                   'daily_call_report_id',
                                   string="Managers")
    partner_id = fields.Many2one('res.partner', 'Partner')
    city_id = fields.Many2one("setu.pharma.city", string="City")
    doctor_products = fields.One2many('setu.pharma.employee.daily.call.line.doctor.products',
                                      'dcr_line_id')
    call_type = fields.Selection([
        ('doctor_call', 'Doctor Call'),
        ('chemist_call', 'Chemist Call'),
        ('stockist_call', 'Stockist Call'),
    ], 'Call Type', )
    work_type = fields.Many2one('setu.pharma.work.type', "Work Type")
    distance = fields.Float('Distance')

    @api.depends('call_type', 'city_id')
    @api.onchange('call_type', 'city_id')
    def partner_id_onchange(self):
        """ Prepare Dynamic Domain for Selecting the Partner. """
        domain = [('city_id', '=', self.city_id.id)] if self.city_id else []
        if self.call_type in ['doctor_call', 'chemist_call', 'stockist_call']:
            self.work_type = self.env.ref(
                'setu_pharma_basic.setu_pharma_work_type_RW') and self.env.ref(
                'setu_pharma_basic.setu_pharma_work_type_RW').id or False
        if self.call_type == 'doctor_call':
            return {'domain': {'partner_id': [('is_doctor', '=', True)] + domain}}
        if self.call_type == 'chemist_call':
            return {'domain': {'partner_id': [('is_chemist', '=', True)] + domain}}
        if self.call_type == 'stockist_call':
            return {'domain': {'partner_id': [('is_stockist', '=', True)] + domain}}
        else:
            return {'domain': {'partner_id': domain}}

    def add_product_with_quantity(self):
        wiz_action = self.env.ref('setu_pharma_basic.dcr_product_selection_wizard_action').read()[0]
        view_id = self.env.ref('setu_pharma_basic.view_dcr_product_selection_wizard_form')
        wiz_obj = self.env['dcr.line.product.selection.wizard']
        wiz_obj = wiz_obj.create(
            {
                'dcr_line': self.id, 'partner_id': self.partner_id.id,
                'dcr_selection_lines': [(0, 0, {'product_id': i.product_id.id,
                                                'quantity': i.quantity}) for i in
                                        self.doctor_products]})
        wiz_action['view_id'] = view_id.id
        wiz_action['res_id'] = wiz_obj.id
        return wiz_action

    @api.model
    def create(self, vals):
        ctx = self.env.context
        if ctx.get('default_dcr_id'):
            dcr_id = ctx.get('default_dcr_id')
        else:
            dcr_id = self.dcr_id.search([
                ('call_date', '=', datetime.date.today())]
                , limit=1).id
        if 'call_type' in vals and vals.get('call_type') in ['doctor_call', 'chemist_call',
                                                             'stockist_call']:
            vals.update(
                {'work_type': self.env.ref(
                    'setu_pharma_basic.setu_pharma_work_type_RW') and self.env.ref(
                    'setu_pharma_basic.setu_pharma_work_type_RW').id or False})
        if 'dcr_id' not in vals:
            vals.update({'dcr_id': dcr_id})
        return super(EmployeeDailyCallReportLine, self).create(vals)

    def write(self, vals):
        if 'call_type' in vals and vals.get('call_type') in ['doctor_call', 'chemist_call',
                                                             'stockist_call']:
            vals.update(
                {'work_type': self.env.ref(
                    'setu_pharma_basic.setu_pharma_work_type_RW') and self.env.ref(
                    'setu_pharma_basic.setu_pharma_work_type_RW').id or False})
        return super(EmployeeDailyCallReportLine, self).write(vals)

    @api.onchange('city_id')
    def onchange_city(self):
        for line in self:
            city = line.dcr_id.headquarter_id.ex_headquarter_ids.filtered(lambda city: city.city_id.id == line.city_id.id)
            line.distance = city.distance


class EmployeeDailyCallReportLineDoctor(models.Model):
    _name = 'setu.pharma.employee.daily.call.line.doctor.products'
    _rec_name = 'dcr_line_id'
    _description = "setu.pharma.employee.daily.call.line.doctor.products"

    dcr_line_id = fields.Many2one('setu.pharma.employee.daily.call.line', 'DCR Line Reference')
    product_id = fields.Many2one('product.product', 'Product')
    quantity = fields.Integer('Quantity')

    def name_get(self):
        """ DCR Product Name Preparation """
        dcr_product_names = []
        for dcr_product in self:
            dcr_product_names.append((dcr_product.id, "%s - %s" % (dcr_product.product_id.name,
                                                                   dcr_product.quantity)))
        return dcr_product_names
