
from odoo import models, fields, api, _

class SdHrHolidaysLeave(models.Model):
    _inherit = "hr.leave"

    registered = fields.Boolean()