from odoo import fields, models

class DailyFinanceSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    finance_account_sid = fields.Char(
        string='Twilio Account SID',
        config_parameter='twilio.account_sid_finance'
    )

    finance_auth_token = fields.Char(
        string='Twilio Auth Token',
        config_parameter='twilio.auth_token_finance'
    )

    finance_mobile = fields.Char(
        string='Twilio Mobile',
        config_parameter='twilio.mobile_finance',
        default="+14155238886"
    )