from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    approval_request = fields.Reference(company_dependent=True,
                                        string='Approval Request For',
                                        selection='_selection_target_model')

    @api.model
    def _selection_target_model(self):
        """
        Use: This method will prepare all model name for approval request
        """
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([])]

    def action_confirm(self):
        """
           This method also raise error in when tour plan line is empty
        """
        if self.approval_request._name == 'setu.pharma.tour.plan':
            if not self.approval_request.tour_plan_lines:
                raise ValidationError(_("Tourplan line is mandatory Generate or Add TP line"))
        return super(ApprovalRequest, self).action_confirm()
