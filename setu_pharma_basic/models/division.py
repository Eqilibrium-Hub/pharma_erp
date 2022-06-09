from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class Division(models.Model):
    _name = 'setu.pharma.division'
    _description = "Pharma Division"

    # Default Methods
    def _default_company_sets(self):
        """ Set default company for new Division created. """
        return self.env.company

    name = fields.Char(string="Division Name", copy=False)
    code = fields.Char(string="Division Code", copy=False, size=5)
    product_ids = fields.One2many("product.product", "division_id", string="Products", copy=False)
    employee_ids = fields.One2many("hr.employee", "division_id", string="Employees", copy=False)
    designation_ids = fields.Many2many("setu.pharma.designation", "division_designation_relation",
                                       "designation_id",
                                       "division_id", string="Designations", copy=False)
    company_id = fields.Many2one("res.company", string="Company", default=_default_company_sets)
    active = fields.Boolean(string="Active Division", default=True,
                            help="Currently Active Division.")
    headquarter_ids = fields.Many2many(comodel_name="setu.pharma.headquarters",
                                       relation="pharma_division_headquarter_rel",
                                       column1='division_id', column2='headquarter_id',
                                       string="Headquarters")
    # Computed Fields for Count
    total_headquarters = fields.Integer(string="Total Headquarters", compute="_compute_total_count",
                                        store=True)
    total_employees = fields.Integer(string="Total Employees", compute="_compute_total_count",
                                     store=True)
    total_products = fields.Integer(string="Total Products", compute="_compute_total_count",
                                    store=True)

    @api.depends('headquarter_ids', 'employee_ids', 'product_ids')
    def _compute_total_count(self):
        """ Calculate the total count of the ``x2Many`` fields. """
        for division in self:
            division.total_headquarters = division.headquarter_ids and len(
                division.mapped('headquarter_ids')) or 0
            division.total_employees = division.employee_ids and len(
                division.mapped('employee_ids')) or 0
            division.total_products = division.product_ids and len(
                division.mapped('product_ids')) or 0

    @api.constrains('code')
    def _check_division_code(self):
        """ Check constrains for same Division Code. """
        for division in self:
            if self.with_context(active_test=False).search([
                ('code', '=ilike', division.code),
                ('id', '!=', division.id),
            ]):
                raise ValidationError(
                    _("Duplicate Division Code Found.\nPlease Add Different Division Code"))

    def action_view_records(self):
        """ Open Records for XML button with dynamic context. """
        record_ids = []
        action, view_id = self.env['setu.pharma.headquarters'].get_action_and_view_id()
        if self._context.get('open_headquarters'):
            record_ids = self.headquarter_ids and self.headquarter_ids.ids
        if self._context.get('open_products'):
            record_ids = self.product_ids and self.product_ids.ids
        if self._context.get('open_employees'):
            record_ids = self.employee_ids and self.employee_ids.ids
        action = self.env['setu.pharma.headquarters']._prepare_context_for_count_fields(action)
        if record_ids:
            action['domain'] = [('id', 'in', record_ids)]
            action['views'] = [(view_id.id, 'tree'), (False, 'form')]
            return action

    @api.model
    def create(self, vals):
        """
         ->Whenever the Division created, System will Update code to upper.
         ->To write divsions in designation field
        """
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        result = super(Division, self).create(vals)

        for designation in result.designation_ids:
            designation.write({'division_ids': [(4, result.id)]})
        return result

    def write(self, vals):
        """
           -> Whenever the Division updated, System will Update code to upper.
           -> To set division in designation field
        """
        if vals.get('code'):
            vals['code'] = vals['code'].upper()

        difference = False
        if vals.get('designation_ids'):
            old_designations = self.designation_ids
            vals_designation = vals['designation_ids'][0][2]
            difference = set(old_designations.ids) - set(vals_designation)
        result = super(Division, self).write(vals)
        for division in self:
            division.designation_ids.division_ids = [(4, division.id, _)]
        if difference:
            self.env['setu.pharma.designation'].browse(difference).division_ids = [(3, div.id) for div in self]
        return result
