from odoo import fields, models, api, _

class FinanceReportWizard(models.TransientModel):
    _name = 'finance.report.wizard'

    partner_id = fields.Many2one('res.partner', default=lambda self: self.env.user.partner_id)
    select_all = fields.Boolean()
    start_date = fields.Date()
    end_date = fields.Date()

    def create_report(self):
        condition = [('partner_id', '=', self.partner_id.id)]
        if not self.select_all and (self.start_date and self.end_date):
            condition = [
                ('partner_id', '=', self.partner_id.id),
                ('date', '>=', self.start_date),
                ('date', '<=', self.end_date)
            ]
            
        daily_finance_ids = self.env['daily.finance'].search(condition)
        
        if daily_finance_ids:
            report_lines = []
            finance_type = ['income', 'outcome']
            for ft in finance_type:
                list_usage = ['food', 'salary', 'entertain', 'bill', 'charity', 'other']
                usage_info = {}
                for usage in list_usage:
                    filter_by_usage = daily_finance_ids.filtered(lambda x: x.type == ft and x.usage == usage)
                    value = ""
                    if filter_by_usage:
                        total_amount_usage = sum(usg.total for usg in filter_by_usage)
                        value = "%sx (Rp %s)" % (len(filter_by_usage), f'{total_amount_usage:,}')

                    usage_info[usage] = value

                total_type = sum(df.total for df in daily_finance_ids.filtered(lambda x: x.type == ft))
                report_lines.append((0, 0, {
                    'type': ft,
                    'food': usage_info['food'],
                    'salary': usage_info['salary'],
                    'entertain': usage_info['entertain'],
                    'bill': usage_info['bill'],
                    'charity': usage_info['charity'],
                    'other': usage_info['other'],
                    'total': total_type
                }))
            
            all_datas = self.env['daily.finance'].search([('partner_id', '=', self.partner_id.id)])
            total_outcome = sum(df.total for df in all_datas.filtered(lambda x: x.type == 'outcome'))
            total_income = sum(df.total for df in all_datas.filtered(lambda x: x.type == 'income'))

            sub_total = sum(data.total for data in daily_finance_ids.filtered(lambda x: x.type == 'income')) - \
                sum(data.total for data in daily_finance_ids.filtered(lambda x: x.type == 'outcome'))

            create_finance_report = self.env['finance.report'].create({
                'partner_id': self.partner_id.id,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'report_line_ids': report_lines,
                'sub_total': sub_total,
                'total_balance': total_income - total_outcome
            })

            return create_finance_report.id

        return False