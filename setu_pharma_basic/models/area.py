from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class Area(models.Model):
    _name = 'setu.pharma.area'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Division and City Wise Area Records."

    # Default Methods
    def _default_company_sets(self):
        """ Set default company. """
        return self.env.company

    def _default_requester(self):
        """ Set default user. """
        return self.env.user

    # Fields Declaration
    name = fields.Char(string="Area Name", help="Area Name.")
    code = fields.Char(string="Code", help="Area Code.", copy=False,
                       tracking=True)
    pincode = fields.Char(string="PIN", help="Postal Code For The Area.", tracking=True)
    state = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], tracking=True,
        compute="_compute_state", string="Status", depends=['approval_request_id.request_status'],
        copy=False, default='new', help="Approving status")
    approval_request_id = fields.Many2one('approval.request', "Approval Request", tracking=True)
    requester_id = fields.Many2one("res.users", string="Requester", default=_default_requester,
                                   help="Requester Name")
    division_id = fields.Many2one("setu.pharma.division", string="Division",
                                  help="Division To Map With Area", copy=False, tracking=True)
    company_id = fields.Many2one("res.company", string="Company", default=_default_company_sets)
    active = fields.Boolean(string="Active Area", default=True, help="Currently Active Area.")

    headquarter_id = fields.Many2one('setu.pharma.headquarters', 'Headquarter' , tracking=True)
    city_id = fields.Many2one('res.city', 'City' , tracking=True)

    def _compute_state(self):
        """ Compute State for area. """
        for area in self:
            area.state = area.approval_request_id.request_status or area.state

    @api.constrains('code')
    def _check_area_code(self):
        """ Check constrains for same Area Code. """
        for area in self:
            if self.with_context(active_test=False).search([
                ('code', '=ilike', area.code),
                ('id', '!=', area.id),
            ]):
                raise ValidationError(_("Duplicate Area Code Found.\nPlease Add Different Area."))

    @api.model
    def create(self, vals):
        """ Whenever the Area created, System will create an Approval Record."""
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        area = super(Area, self).create(vals)
        if area:
            approval_category = self.env.ref(
                'setu_pharma_basic.approval_category_data_area_approval')
            area.create_approval_request_and_confirm(approval_category, model_record=area)
        return area

    def write(self, vals):
        """ Whenever the Area updated, System will Update code to upper."""
        if vals.get('code'):
            vals['code'] = vals['code'].upper()
        return super(Area, self).write(vals)

    def create_approval_request_and_confirm(self, approval_category, model_record):
        """ Create Approval Request and Confirm that request. """
        approval_obj = self.env['approval.request']
        if approval_category.automated_sequence:
            name = approval_category.sequence_id.next_by_id()
        else:
            name = model_record.name
        msg = """<html><head></head><body>
        Hi,
        <br/>I've Created a New '{model}' as <b>{record}</b>.
        <br/>
        Thank You.
        </body></html>""".format(model=model_record._description, record=model_record.name)
        try:
            approval_id = approval_obj.create({
                'name': name,
                'category_id': approval_category.id,
                'request_owner_id': model_record.requester_id.id,
                'reason': msg,
                'approval_request': '%s,%s' % (model_record._name, model_record.id)
            })
            model_record.approval_request_id = approval_id.id
        except Exception as create_error:
            raise ValidationError(_("Approval Request Creation Error: {}".format(create_error)))
        try:
            approval_id.action_confirm()
        except Exception as confirm_error:
            raise ValidationError(_("Approval Request Confirm Error: {}".format(confirm_error)))

    def name_get(self):
        """ Area Name Preparation """
        area_names = []
        for area in self:
            pin = area.pincode and "- %s" % area.pincode or ''
            city = area.city_id and "(%s)" % area.city_id.name or ''
            area_names.append((area.id, "%s %s %s" % (area.name, city, pin)))
        return area_names
