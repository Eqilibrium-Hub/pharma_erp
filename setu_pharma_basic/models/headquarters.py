from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class SetuPharmaHeadquarters(models.Model):
    _name = 'setu.pharma.headquarters'
    _description = 'All Headquarters listed in this models.'

    name = fields.Char(string='Name', copy=False,
                       index=True, default=lambda self: _('New'))
    code = fields.Char(string='HQ Code', copy=False, size=5)
    area_id = fields.Many2one('setu.pharma.area', 'Area')
    city_id = fields.Many2one("setu.pharma.city", string="City")
    ex_headquarter_ids = fields.One2many("setu.pharma.ex.headquarter", "headquarter_id",
                                         string='Ex. Headquarters')
    division_id = fields.Many2one('setu.pharma.division', string='Division')
    company_id = fields.Many2one("res.company", string="Company",
                                 default=lambda self: self.env.company)

    active = fields.Boolean(string="Active", default=True,
                            help="Currently Active Headquarters.")
    employee_ids = fields.Many2many("hr.employee", string='Employees')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    employee_location_ids = fields.One2many("stock.location", 'headquarter_id',
                                            string='Stock Locations', required=0)
    # Computed Fields for Count
    total_employees = fields.Integer(string="Total Employees", compute="_compute_total_count",
                                     store=True)
    total_of_ex_headquarters = fields.Integer(string="Total Ex. Headquarters",
                                              compute="_compute_total_count",
                                              store=True)
    total_employee_locations = fields.Integer(string="Total Locations",
                                              compute="_compute_total_count",
                                              store=True)

    @api.depends('employee_ids', 'ex_headquarter_ids', 'employee_location_ids')
    def _compute_total_count(self):
        for hq in self:
            hq.total_employees = hq.employee_ids and len(hq.mapped('employee_ids')) or 0
            hq.total_of_ex_headquarters = hq.ex_headquarter_ids and len(
                hq.mapped('ex_headquarter_ids')) or 0
            hq.total_employee_locations = hq.employee_location_ids and len(
                hq.mapped('employee_location_ids')) or 0

    def action_view_records(self):
        """ Open Records for XML button with dynamic context. """
        record_ids = []
        action, view_id = self._get_action_and_view_id()
        action = self._prepare_context_for_count_fields(action)
        if self._context.get('open_employees'):
            record_ids = self.mapped('employee_ids') and self.mapped('employee_ids').ids
        elif self._context.get('open_ex_headquarters'):
            record_ids = self.mapped('ex_headquarter_ids') and self.mapped('ex_headquarter_ids').ids
        elif self._context.get('open_employee_stock_locations'):
            record_ids = self.mapped('employee_location_ids') and self.mapped(
                'employee_location_ids').ids
        action['domain'] = [('id', 'in', record_ids)]
        action['view_id'] = view_id.id
        return action

    def _get_action_and_view_id(self):
        """ Prepare Action and View for XML button with dynamic context. """
        view_id = self.env['ir.ui.view']
        action = self.env['ir.actions.act_window']
        if self._context.get('open_employees'):
            view_id = self.env.ref("hr.view_employee_tree")
            action = self.env.ref('hr.open_view_employee_tree').read()[0]
        elif self._context.get('open_ex_headquarters'):
            view_id = self.env.ref("setu_pharma_basic.setu_pharma_city_list")
            action = self.env.ref('setu_pharma_basic.setu_pharma_city_action_window').read()[0]
        elif self._context.get('open_employee_stock_locations'):
            view_id = self.env.ref("stock.view_location_tree2")
            action = self.env.ref('stock.action_location_form').read()[0]
        elif self._context.get('open_headquarters'):
            view_id = self.env.ref("setu_pharma_basic.setu_pharma_headquarters_tree_view")
            action = self.env.ref('setu_pharma_basic.setu_pharma_headquarters_act_window').read()[0]
        elif self._context.get('open_products'):
            view_id = self.env.ref("product.product_product_tree_view")
            action = self.env.ref('stock.stock_product_normal_action').read()[0]
        return action, view_id

    def _prepare_context_for_count_fields(self, action):
        """ Prepare general context for the Views are opening from Smart Buttons """
        ctx = self._context.copy()
        ctx.update({"create": False, "edit": False, 'delete': False})
        action['view_mode'] = 'tree,form'
        action['context'] = ctx
        return action

    def button_employees_stock_location(self):
        for hq in self:
            # We will create locations for Employees without locations.
            employees_wo_locations = hq.employee_ids.filtered(lambda x: not x.stock_location_id)
            for employee in employees_wo_locations:
                location = self.env['stock.location'].create({
                    'employee_id': employee.id,
                    'name': employee.name + ' - ' + hq.division_id.name,
                    'location_id': hq.warehouse_id.lot_stock_id.id,
                    'division_id': employee.division_id.id
                })
                hq.employee_location_ids += location
                employee.stock_location_id = location.id

    @api.constrains('code')
    def _check_duplicate_headquarter_code(self):
        """ Check constrains for same Headquarters Code. """
        for headquarter in self:
            if self.with_context(active_test=False).search([
                ('code', '=ilike', headquarter.code),
                ('id', '!=', headquarter.id),

            ]):
                raise ValidationError(_("Duplicate Headquarter Code Found.\n"
                                        "Please Add Different Code for Headquarter."))

    @api.constrains('city_id', 'division_id', 'area_id')
    def _check_division_city_unique(self):
        for hq in self:
            duplicate_record = self.with_context(active_test=False).search([
                ('city_id', '=', hq.city_id.id),
                ('area_id', '=', hq.area_id.id),
                ('division_id', '=', hq.division_id.id),
                ('id', '!=', hq.id),
            ])
            if duplicate_record:
                raise ValidationError(_("Duplicate Headquarter Code Found with Same City and "
                                        "Division: '{}'\n".format(
                    ','.join(duplicate_record.mapped('name')))))

    @api.model
    def create(self, vals):
        """ To create a new warehouse when new headquarter is created. """
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        if vals.get('division_id') and vals.get('city_id'):
            div = self.env['setu.pharma.division'].browse(vals.get('division_id'))
            div_name = div.name
            city = self.env['setu.pharma.city'].browse(vals.get('city_id'))
            city_name = city.name
            vals['name'] = city_name + ' - ' + div_name

        headquarter = super(SetuPharmaHeadquarters, self).create(vals)
        if headquarter:
            warehouse = self.env['stock.warehouse']
            warehouse = warehouse.create({
                'name': headquarter.name + ' - Warehouse',
                'code': headquarter.code,
                'headquarter_id': headquarter.id,
            })
            headquarter.warehouse_id = warehouse.id
            headquarter.employee_ids.headquarter_id = headquarter.id
            headquarter.division_id.headquarter_ids = [(4, headquarter.id, _)]
        return headquarter

    def write(self, vals):
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        for headquarter in self:
            headquarter.employee_ids.headquarter_id = self.id
            if headquarter.division_id:
                headquarter.division_id.headquarter_ids = [(4, headquarter.id, _)]

        return super(SetuPharmaHeadquarters, self).write(vals)

    def name_get(self):
        """ Headquarter Name Preparation """
        hq_names = []
        for hq in self:
            division = hq.division_id and "- %s" % hq.division_id.name or ''
            area = hq.area_id and "(%s)" % hq.area_id.name or ''
            hq_names.append((hq.id, "%s %s %s" % (hq.name, division, area)))
        return hq_names

    # @api.constrains('ex_headquarter_ids')
    # def unique_city(self):
    #     for headquater in self:
    #         city = headquater.headquarter_id.ex_headquarter_ids.filtered(
    #             lambda city: headquater.city_id in city.city_id)
    #         if city:
    #             raise UserError(_('city already exists !!!'))