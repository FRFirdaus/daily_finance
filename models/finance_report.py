from odoo import fields, models, api, _

class FinanceReport(models.Model):
    _name = 'finance.report'

    partner_id = fields.Many2one('res.partner')
    start_date = fields.Date()
    end_date = fields.Date()
    report_line_ids = fields.One2many('finance.report.line', 'finance_report_id')
    sub_total = fields.Float(digits = (12,2), readonly=True)
    total_balance = fields.Float(digits = (12,2), readonly=True)

    def _get_report_base_filename(self):
        return self.display_name

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "[Report] %s | %s" % (
                self.partner_id.name,
                self.create_date
            )))

        return result

class FinanceReportLine(models.Model):
    _name = 'finance.report.line'

    finance_report_id = fields.Many2one('finance.report', ondelete="cascade")
    type = fields.Selection([
        ('income', 'Income'),
        ('outcome', 'Outcome')
    ])

    food = fields.Char()
    salary = fields.Char()
    entertain = fields.Char()
    bill = fields.Char()
    charity = fields.Char()
    other = fields.Char()

    total = fields.Float()