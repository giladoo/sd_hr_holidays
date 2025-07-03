from odoo import models, fields, api, _
from datetime import datetime
import pytz

class SdHrFormsHourlyLeave(models.Model):
    _name = 'sd_hr_holidays.hourly_leave'
    _description = 'Hourly Leaves'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    state = fields.Selection([('new', 'New'),
                              ('approved', 'Approved'),
                              ('hold', 'Hold'),
                              ('canceled', 'Canceled'),
                              ('registered', 'Registered'),], default='new')
    employee_id = fields.Many2one('hr.employee', default=lambda self: self.env.user.employee_id, required=True)
    department_id = fields.Many2one(related='employee_id.department_id')
    approvers = fields.Many2many(related='employee_id.sd_hourly_approvers')
    request_date = fields.Date(default=lambda self: datetime.now(pytz.timezone(self._context.get('tz') or 'UTC')),)

    request_date_from = fields.Date('Request Start Date')
    request_date_to = fields.Date('Request End Date')
    # Interface fields used when using hour-based computation
    request_hour_from = fields.Float(string='Hour from')
    request_hour_to = fields.Float(string='Hour to')