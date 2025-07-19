
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from collections import namedtuple, defaultdict
from datetime import datetime, timedelta, time
from odoo.addons.resource.models.utils import float_to_time, HOURS_PER_DAY
from math import ceil
from icecream import ic

class SdHrHolidaysLeave(models.Model):
    _inherit = "hr.leave"

    registered = fields.Boolean()

    def action_validate(self, check_state=True):
        current_employee = self.env.user.employee_id
        leaves = self._get_leaves_on_public_holiday()
        # Giladoo
        if not self.holiday_status_id.mission and leaves:
            raise ValidationError(_('The following employees are not supposed to work during that period:\n %s') % ','.join(leaves.mapped('employee_id.name')))
        if check_state and any(holiday.state not in ['confirm', 'validate1'] and holiday.validation_type != 'no_validation' for holiday in self):
            raise UserError(_('Time off request must be confirmed in order to approve it.'))
        self.write({'state': 'validate'})

        leaves_second_approver = self.env['hr.leave']
        leaves_first_approver = self.env['hr.leave']

        for leave in self:
            if leave.validation_type == 'both':
                leaves_second_approver += leave
            else:
                leaves_first_approver += leave

        leaves_second_approver.write({'second_approver_id': current_employee.id})
        leaves_first_approver.write({'first_approver_id': current_employee.id})

        self._validate_leave_request()
        if not self.env.context.get('leave_fast_create'):
            self.filtered(lambda holiday: holiday.validation_type != 'no_validation').activity_update()
        return True

    def _get_durations(self, check_leave_type=True, resource_calendar=None):
        """
        This method is factored out into a separate method from
        _compute_duration so it can be hooked and called without necessarily
        modifying the fields and triggering more computes of fields that
        depend on number_of_hours or number_of_days.
        """
        result = {}
        employee_leaves = self.filtered('employee_id')
        employees_by_dates_calendar = defaultdict(lambda: self.env['hr.employee'])
        for leave in employee_leaves:
            if not leave.date_from or not leave.date_to:
                continue
            employees_by_dates_calendar[(leave.date_from, leave.date_to, leave.holiday_status_id.include_public_holidays_in_duration, resource_calendar or leave.resource_calendar_id)] += leave.employee_id
        # We force the company in the domain as we are more than likely in a compute_sudo
        domain = [('time_type', '=', 'leave'),
                  ('company_id', 'in', self.env.companies.ids + self.env.context.get('allowed_company_ids', [])),
                  # When searching for resource leave intervals, we exclude the one that
                  # is related to the leave we're currently trying to compute for.
                  '|', ('holiday_id', '=', False), ('holiday_id', 'not in', employee_leaves.ids)]
        # Precompute values in batch for performance purposes
        work_time_per_day_mapped = {
            (date_from, date_to, calendar): employees.with_context(
                    compute_leaves=not include_public_holidays_in_duration)._list_work_time_per_day(date_from, date_to, domain=domain, calendar=calendar)
            for (date_from, date_to, include_public_holidays_in_duration, calendar), employees in employees_by_dates_calendar.items()
        }
        work_days_data_mapped = {
            (date_from, date_to, calendar): employees._get_work_days_data_batch(date_from, date_to, compute_leaves=not include_public_holidays_in_duration, domain=domain, calendar=calendar)
            for (date_from, date_to, include_public_holidays_in_duration, calendar), employees in employees_by_dates_calendar.items()
        }
        for leave in self:
            calendar = resource_calendar or leave.resource_calendar_id
            if not leave.date_from or not leave.date_to or not calendar:
                result[leave.id] = (0, 0)
                continue
            if calendar.flexible_hours:
                days = (leave.date_to - leave.date_from).days + (1 if not leave.request_unit_half else 0.5)
                public_holidays = self.env['resource.calendar.leaves'].search([
                    ('resource_id', '=', False),
                    ('calendar_id', '=', calendar.id),
                    ('date_from', '<=', leave.date_to),
                    ('date_to', '>=', leave.date_from)
                ])
                excluded_days = sum(
                    (min(holiday.date_to, leave.date_to) - max(holiday.date_from, leave.date_from)).days + 1
                    for holiday in public_holidays
                )
                days = days - excluded_days
                hours = min(leave.request_hour_to - leave.request_hour_from, calendar.hours_per_day) if leave.request_unit_hours \
                    else (days * calendar.hours_per_day)
                result[leave.id] = (days, hours)
                continue
            hours, days = (0, 0)
            if leave.employee_id:
                if leave.employee_id.is_flexible and leave.leave_type_request_unit in ['day','half_day']:
                    duration = leave.date_to - leave.date_from
                    days = ceil(duration.total_seconds() / (24 * 3600))
                elif leave.leave_type_request_unit == 'day' and check_leave_type:
                    # list of tuples (day, hours)
                    work_time_per_day_list = work_time_per_day_mapped[(leave.date_from, leave.date_to, calendar)][leave.employee_id.id]
                    days = len(work_time_per_day_list)
                    hours = sum(map(lambda t: t[1], work_time_per_day_list))
                else:
                    # Giladoo
                    if leave.holiday_status_id.mission:
                        mission_calendar = leave.holiday_status_id.mission_calendar
                        work_days_data = leave.employee_id._get_work_days_data_batch(leave.date_from, leave.date_to, calendar=mission_calendar )[ leave.employee_id.id]
                        hours, days = work_days_data['hours'], work_days_data['days']
                    else:

                        work_days_data = work_days_data_mapped[(leave.date_from, leave.date_to, calendar)][
                            leave.employee_id.id]
                        hours, days = work_days_data['hours'], work_days_data['days']
            else:
                today_hours = calendar.get_work_hours_count(
                    datetime.combine(leave.date_from.date(), time.min),
                    datetime.combine(leave.date_from.date(), time.max),
                    False)
                hours = calendar.get_work_hours_count(leave.date_from, leave.date_to, compute_leaves=not leave.holiday_status_id.include_public_holidays_in_duration)
                days = hours / (today_hours or HOURS_PER_DAY)
            if leave.leave_type_request_unit == 'day' and check_leave_type:
                days = ceil(days)
            result[leave.id] = (days, hours)

        return result


# def time_difference(self, dt1, dt2):
#     # Ensure dt1 is earlier than dt2
#     if dt2 < dt1:
#         dt1, dt2 = dt2, dt1
#
#     delta = dt2 - dt1
#     total_minutes = delta.total_seconds() // 60
#     hours = int(total_minutes // 60)
#     minutes = int(total_minutes % 60)
#
#     return hours, minutes

class SdHrHolidaysLeave(models.Model):
    _inherit = "hr.leave.type"

    mission = fields.Boolean()
    mission_calendar = fields.Many2one('resource.calendar')
