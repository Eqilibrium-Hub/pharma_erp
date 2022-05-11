from odoo import api, fields, models, _


class EmployeeSamplingAndGiftReporting(models.Model):
    _name = 'setu.pharma.stock.distribution'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Records Of Stock Distribution For The Sample or Gifted Products."

    name = fields.Char(string='Sampling And Gift Reference', required=True, copy=False,
                       readonly=True,
                       index=True, default=lambda self: _('New'))
    line_ids = fields.One2many("setu.pharma.stock.distribution.line", "distribution_id",
                               string="Distribution lines")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    distribution_date = fields.Date(string="Distribution date", copy=False,
                                    default=fields.Date.today())
    partner_id = fields.Many2one("res.partner", string="Doctor")
    is_gift_distribution = fields.Boolean(string="Gift Distribution")
    is_sample_distribution = fields.Boolean(string="Sample Distribution")
    division_id = fields.Many2one("setu.pharma.division", string="Division", copy=False)
    company_id = fields.Many2one("res.company", string="Company",
                                 default=lambda self: self.env.company, required=True, readonly=True)
    total_amount = fields.Float(string='Total Amount', compute="_compute_total_amount")

    @api.model
    def create(self, vals_list):
        """
        Functionality:
            - Create New Record Name Based on the sequence.
        """
        if vals_list.get('name', _('New')) == _('New'):
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'setu.pharma.stock.distribution.seq') or _('New')
        return super(EmployeeSamplingAndGiftReporting, self).create(vals_list)

    @api.depends('line_ids.subtotal')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('subtotal')) or record.total_amount
