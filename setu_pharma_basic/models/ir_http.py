# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, http, models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        """
        Added By: Mitrarajsinh Jadeja | Date: 29th Apr,2021
        Use: Added Division Data in the Odoo Session
        """
        user = request.env.user
        session_info = super(IrHttp, self).session_info()
        # division_ids = self.env['setu.pharma.division'].search([])
        session_info.update({
            "user_divisions": {
                'current_division': user.employee_id.division_id.id,
                'allowed_divisions': {
                    division.id: {
                        'id': division.id,
                        'name': division.name,
                    } for division in user.division_ids + user.employee_id.division_id
                },
            },
            "show_effect": True,
            "display_switch_division_menu": True,
        })
        return session_info
