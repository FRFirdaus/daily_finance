from odoo import api, fields, models, exceptions, _
from odoo.exceptions import AccessDenied

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    password_user = fields.Char()
