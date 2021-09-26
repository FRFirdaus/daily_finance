from odoo import fields, models, api, _
from datetime import datetime

class DailyFinance(models.Model):
    _name = 'daily.finance'
    _inherit = ['mail.thread']

    partner_id = fields.Many2one('res.partner', required=True, default=lambda self: self.env.user.partner_id)
    type = fields.Selection([
        ('income', 'Income'),
        ('outcome', 'Outcome')
    ])

    total = fields.Float()
    usage = fields.Selection([
        ('food', 'Food'),
        ('salary', 'Salary'),
        ('entertain', 'Entertainment'),
        ('bill', 'Monthly Bill'),
        ('charity', 'Charity'),
        ('other', 'Other')
    ])

    date = fields.Date(default=datetime.now().strftime('%Y-%m-%d'))

    balance = fields.Float(compute="_compute_total_balance")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)

    description = fields.Text()

    emoji = fields.Selection([
        ('income', '\U0001f60e'),
        ('outcome', '\U0001f62d')
    ], compute="_compute_emoji")
    
    loan_type = fields.Selection([
        ('loan', 'Loan'),
        ('payment', 'Payment')
    ])

    matching_code = fields.Char()
    matching_loan_id = fields.Many2one(_name)

    @api.onchange('matching_loan_id', 'loan_type')
    def matching_loan_data(self):
        if self.matching_loan_id:
            self.matching_code = self.matching_loan_id.matching_code

    @api.constrains('loan_type')
    def matching_loan_finance(self):
        if self.loan_type and self.loan_type == 'loan':
            matching_code = "LN%s" % (self.id)
            self.matching_code = matching_code

    def _compute_emoji(self):
        for rec in self:
            rec.emoji = 'income'
            if rec.type == 'outcome':
                rec.emoji = 'outcome'

    def _compute_total_balance(self):
        for rec in self:
            rec.balance = rec.total
            if rec.type == 'outcome':
                rec.balance = rec.total * -1

    def name_get(self):
        result = []
        for rec in self:
            if not rec.loan_type:
                result.append((rec.id, "[%s] %s | %s | %s for %s" % (
                    rec.type, 
                    rec.partner_id.name, 
                    rec.date,
                    rec.total,
                    rec.usage
                )))
            else:
                result.append((rec.id, "[%s][%s/%s] %s | %s | %s for %s" % (
                    rec.type,
                    "LOAN" if rec.loan_type == 'loan' else "PAYMENT",
                    rec.matching_code,
                    rec.partner_id.name, 
                    rec.date,
                    rec.total,
                    rec.usage
                )))

        return result