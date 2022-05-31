from odoo import models, fields, _


class StockWarehouseExtends(models.Model):
    _inherit = 'stock.warehouse'

    headquarter_id = fields.Many2one("setu.pharma.headquarters", string="Headquarter",
                                     copy=False)
    is_depo_warehouse = fields.Boolean(string="Depo warehouse ?", copy=False)
    depo_manager_id = fields.Many2one("res.users", string="Depo manager", copy=False)
    employee_ids = fields.Many2many("hr.employee", "stock_warehouse_employees_relation",
                                    "stock_warehouse_id",
                                    "employee_id", string="Employees")
    division_id = fields.Many2one(related='headquarter_id.division_id', string="Division",
                                  copy=False)
    city_id = fields.Many2one(related='headquarter_id.city_id', string="City", copy=False)
    code = fields.Char(size=8, store=True, compute="_compute_hq_code",
                       inverse='_inverse_hq_code')

    def _compute_hq_code(self):
        """ Update Related Headquarter Code while updating in the warehouse. """
        for wh in self:
            if wh.headquarter_id and wh.headquarter_id.code:
                wh.code = wh.headquarter_id.code
            else:
                wh.code = wh.code

    def _inverse_hq_code(self):
        """ Update Related Headquarter Code while updating in the warehouse. """
        for wh in self:
            if wh.headquarter_id:
                wh.headquarter_id.code = wh.code
            else:
                wh.headquarter_id.code = wh.code

    def _get_sequence_values(self):
        """ Each picking type is created with a sequence. This method returns
        the sequence values associated to each picking type.
        """
        seq_values = super(StockWarehouseExtends, self)._get_sequence_values()
        seq_values['int_type_id'] = {
            'name': self.name + ' ' + _('Sequence internal'),
            'prefix': self.code + '/STKDIST/', 'padding': 5,
            'company_id': self.company_id.id,
        }
        return seq_values
