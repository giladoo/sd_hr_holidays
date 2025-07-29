
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from collections import namedtuple, defaultdict
from datetime import datetime, timedelta, time
from odoo.addons.resource.models.utils import float_to_time, HOURS_PER_DAY
from math import ceil
from icecream import ic


class SdHrHolidaysMissionDetail(models.Model):
    _name = "sd_hr_holidays.mission_detail"

    leave = fields.Many2one('hr.leave', )
    departure_city = fields.Char()
    return_city = fields.Char()
    project_name = fields.Many2one('sd_projects.projects')

    # departure_date = fields.Datetime(related='leave.request_date_from')
    departure_time = fields.Selection([('morning', 'Morning'),
                                       ('noon', 'Noon'),
                                       ('evening', 'Evening'), ], default='morning', required=True)
    departure_type = fields.Selection([('airplane', 'Airplane'),
                                       ('rail', 'Rail'),
                                       ('bus', 'Bus'),
                                       ('company_car', 'Company Car'),
                                       ('rental_car', 'Rental Car'), ], default='airplane', required=True)

    # return_date = fields.Datetime(related='leave.date_to')
    return_time = fields.Selection([('morning', 'Morning'),
                                    ('noon', 'Noon'),
                                    ('evening', 'Evening'), ], default='evening', required=True)
    return_type = fields.Selection([('airplane', 'Airplane'),
                                       ('rail', 'Rail'),
                                       ('bus', 'Bus'),
                                       ('company_car', 'Company Car'),
                                       ('rental_car', 'Rental Car'), ], default='airplane', required=True)
    residence = fields.Selection([('hotel', 'Hotel'),
                                   ('guest_house', 'Guest House'),
                                   ('camp', 'Camp'),
                                   ('others', 'Others'), ], default='guest_house', required=True)

    description = fields.Text()



