from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_doctor = fields.Boolean(string="Doctor ?", help="Mark If Partner Is Doctor")
    is_stockist = fields.Boolean(string="Stockist ?", help="Mark If Partner Is Stockist")
    is_chemist = fields.Boolean(string="Chemist ?", help="Mark If Partner Is Chemist")
    employee_ids = fields.Many2many("hr.employee",
                                    'setu_pharma_hr_employee_partner_rel',
                                    'partner_id',
                                    'employee_id',
                                    string="Employees")
    degree_tag_ids = fields.Many2many("res.partner.category",
                                      'setu_pharma_partner_category_partner_rel',
                                      'partner_id',
                                      'partner_category_id',
                                      string="Degree")
    speciality_tag_id = fields.Many2one("res.partner.category", string="Speciality")
    area_id = fields.Many2one('setu.pharma.area', string="Area")
    city_id = fields.Many2one('setu.pharma.city', string="Pharma City")
    code = fields.Char(string="Code", size=7)
    doctor_class = fields.Char(string="Class")
    birth_date = fields.Date(string="Date of birth")
    anniversary_date = fields.Date(string="Date of anniversary")
    monthly_visit = fields.Integer(string="Monthly visit")
    is_prescriber = fields.Boolean(string="Prescriber?")
    product_ids = fields.Many2many("product.product",
                                   'setu_pharma_product_product_partner_rel',
                                   'partner_id',
                                   'product_id',
                                   string="Products")
    state = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ],
        compute="_compute_state", string="Status", depends=['approval_request_id'],
        copy=False, store=True, default='new',
        help="Approving status")
    approval_request_id = fields.Many2one('approval.request', "Approval Request")
    requester_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user,
                                   help="Requester Name")
    approver_id = fields.Many2one('res.users', string='Approved by')
    division_ids = fields.Many2many(comodel_name="setu.pharma.division",
                                    relation="hr_partner_res_division_division_rel",
                                    column1='partner_id', column2='division_id', string="Divisions")
    chemist_ids = fields.Many2many(comodel_name="res.partner",
                                   relation="hr_partner_res_partner_chemist_rel",
                                   column1='partner_id', column2='chemist_id', string="Chemists")
    related_employee_ids = fields.One2many('hr.employee.line', 'partner_id')

    def _compute_state(self):
        for partner in self:
            partner.state = partner.approval_request_id.request_status

    @api.constrains('code')
    def _check_partner_code(self):
        """ Check constrains for same Doctor/Stockist/Chemist Code. """
        for partner in self:
            if self.with_context(active_test=False).search([
                ('code', '=ilike', partner.code),
                ('id', '!=', partner.id),
            ]):
                raise ValidationError(_("Duplicate Doctor/Stockist/Chemist Code Found.\n"
                                        "Please Add Different Doctor/Stockist/Chemist Code"))

    @api.model
    def create(self, vals):
        """ Whenever the ResPartner created, System will Update code to upper."""
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        partner = super(ResPartner, self).create(vals)
        if partner:
            approval_category = self.env.ref(
                'setu_pharma_basic.approval_category_data_general_approval')
            self.env['setu.pharma.area'].create_approval_request_and_confirm(approval_category, model_record=partner)
        return partner

    def write(self, vals):
        """ Whenever the ResPartner updated, System will Update code to upper."""
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        return super(ResPartner, self).write(vals)

    def action_view_stockist_monthly_statement(self):

        tree_view_id = self.env.ref('setu_pharma_basic.setu_stockist_monthly_statement_tree_view').id
        form_view_id = self.env.ref('setu_pharma_basic.setu_stockist_monthly_statement_form_view').id

        report_display_tree_views = [(tree_view_id, 'tree'), (form_view_id, 'form')]
        view_mode = "tree,form"

        products = self.env['product.product'].search([('id', 'in', self.product_ids.ids)])
        fiscal_year = self.env['setu.pharma.fiscalyear'].search([('start_year', '=', datetime.now().year)])
        statement = self.env['setu.stockist.monthly.statement'].create({
            'partner_id': self.id,
            'fiscal_period_id': (fiscal_year.period_ids.filtered(lambda x: x.name == datetime.now().strftime('%B'))).id

        })

        for product in products:
            statement.write({
                'stockist_monthly_statement_ids': [(0, 0, {
                    'product_id': product.id
                })]
            })

        return {
            'res_model': 'setu.stockist.monthly.statement',
            'view_mode': view_mode,
            'type': 'ir.actions.act_window',
            'views': report_display_tree_views,
        }

    def action_view_customer_contract(self):
        """
        - To call form view if there are no records of particular doctor
        """
        action = self.env["ir.actions.actions"]._for_xml_id("setu_pharma_basic.action_doctor_support")
        doctor_support_ids = self.env['setu.pharma.monthly.doctor.support'].search([('employee_id', '=', self.id)])

        if not doctor_support_ids:
            action['views'] = [(self.env.ref('setu_pharma_basic.setu_pharma_doctor_action_window_form').id, 'form')]
            action.update({
                'views': [[False, 'form']]})
        else:
            action['domain'] = [('employee_id', '=', self.id)]
        return action
