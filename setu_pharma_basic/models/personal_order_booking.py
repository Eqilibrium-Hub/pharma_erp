import datetime

from odoo import fields, api, models, _


class PersonalOrderBooking(models.Model):
    _name = 'setu.pharma.pob'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Personal Order Booking"

    name = fields.Char(string='Personal Order Booking Reference', copy=False,
                       readonly=True,
                       index=True, default=lambda self: _('New'))
    employee_id = fields.Many2one("hr.employee", string="Employee", copy=False)
    partner_id = fields.Many2one("res.partner", string="Doctor", copy=False)
    total_amount = fields.Float(string="Total amount", compute='_compute_total_amount')
    pob_date = fields.Date(string="Date", copy=False, default=datetime.date.today())
    company_id = fields.Many2one("res.company", string="Company",
                                 default=lambda self: self.env.company)
    division_id = fields.Many2one("setu.pharma.division", string="Division", copy=False)
    note = fields.Char("Note")
    line_ids = fields.One2many("setu.pharma.pob.line", "pob_id", string="POB lines")

    @api.model
    def create(self, vals_list):
        """
        Functionality:
            - Create New Record Name Based on the sequence.
        """
        if vals_list.get('name', _('New')) == _('New'):
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'setu.pharma.pob.seq') or _('New')
        return super(PersonalOrderBooking, self).create(vals_list)

    @api.depends('line_ids.product_id', 'line_ids.quantity', 'line_ids.price_unit')
    def _compute_total_amount(self):
        for pob in self:
            list_subtotal = pob.line_ids.mapped('subtotal')
            if pob.line_ids:
                pob.total_amount = sum(list_subtotal) or pob.total_amount
            else:
                pob.total_amount = pob.total_amount

