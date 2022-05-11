from odoo import models, fields, api, _


class StockistStatement(models.Model):
    _name = "setu.pharma.monthly.closing.process"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Statement of Stockist"

    name = fields.Char(string='Stockist Statement Reference', copy=False,
                       readonly=True,
                       index=True, default=lambda self: _('New'))
    division_id = fields.Many2one("setu.pharma.division", string="Division", copy=False)
    employee_id = fields.Many2one("hr.employee", string="Employee", copy=False)
    company_id = fields.Many2one("res.company", string="Company",
                                 default=lambda self: self.env.company)
    line_ids = fields.One2many("setu.pharma.monthly.closing.process.line", "statement_id",
                               string="Product closing")
    date = fields.Date(string="Date", copy=False)
    partner_id = fields.Many2one("res.partner", string="Stockist", copy=False)

    @api.model
    def create(self, vals_list):
        """
        Functionality:
            - Create New Record Name Based on the sequence.
        """
        if vals_list.get('name', _('New')) == _('New'):
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'setu.pharma.monthly.closing.process.seq') or _('New')
        return super(StockistStatement, self).create(vals_list)
