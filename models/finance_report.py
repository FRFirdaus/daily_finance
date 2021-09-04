from odoo import fields, models, api, _

class FinanceReport(models.Model):
    _name = 'finance.report'

    partner_id = fields.Many2one('res.partner', required=True, default=lambda self: self.env.user.partner_id)
    start_date = fields.Date()
    end_date = fields.Date()
    report_line_ids = fields.One2many('finance.report.line', 'finance_report_id')
    sub_total = fields.Float(digits = (12,2), readonly=True)
    total_balance = fields.Float(digits = (12,2), readonly=True)

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)

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
    
    def generate_pdf_url(self):
		base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
		report_ref = 'daily_finance.finance_pdf_report'
		raport_pdf_name = "Report Finance %s" % (self.partner_id.name)
		return "%s/api/v1/%s/%s/%s" % (
			base_url, 
			report_ref, 
			self.id, 
			raport_pdf_name.replace(" ", "%20")
		)

	def button_preview_pdf(self):
		media_url = self.generate_pdf_url()
		return {                   
			'name'     : 'Preview Report',
			'res_model': 'ir.actions.act_url',
			'type'     : 'ir.actions.act_url',
			'target'   : 'new',
			'url'      : media_url
		}

class FinanceReportLine(models.Model):
    _name = 'finance.report.line'

    finance_report_id = fields.Many2one('finance.report', ondelete="cascade")
    type = fields.Selection([
        ('income', 'Income'),
        ('outcome', 'Outcome')
    ])

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    food = fields.Char()
    salary = fields.Char()
    entertain = fields.Char()
    bill = fields.Char()
    charity = fields.Char()
    other = fields.Char()

    total = fields.Float()