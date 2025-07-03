from odoo import models, fields, api, _


class SdHrFormsHrEmployee(models.Model):
    _inherit = 'hr.employee'

    sd_hourly_approvers = fields.Many2many('res.users', 'sd_hourly_approver', string='Hourly Approvers')
    sd_daily_approvers = fields.Many2many('res.users', 'sd_daily_approver', string='Daily Approvers')

