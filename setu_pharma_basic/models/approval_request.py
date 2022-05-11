from odoo import api, fields, models


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    approval_request = fields.Reference(
        string='Record', selection='_selection_target_model')

    @api.model
    def _selection_target_model(self):
        """
        Use: This method will prepare all model name for approval request
        """
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([])]
