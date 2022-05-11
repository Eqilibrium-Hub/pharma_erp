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
