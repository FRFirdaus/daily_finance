from odoo import http
from odoo.http import request, Response
from twilio.twiml.messaging_response import MessagingResponse

from twilio.rest import Client

class DailyFinanceRequest(http.Controller):
    common_msg = "```Please read the format message! you can type '!help' on the chat to see it.```"

    @http.route('/api/sms', auth='public', csrf=False, methods=['POST'])
    def twilio_whatsapp_message(self):
        body = request.params.get('Body')
        body_split = body.split(" ")
        from_whatsapp_number = request.params.get('From').replace("whatsapp:", "")
        msg = ""
        
        if body == "!help":
            msg = self.message_rules()
            return self.response_message_whatsapp(msg)

        if body_split[0] not in ['set', 'get', 'create', 'delete']:
            msg = "```Please define your purpose in 'set', 'get', 'create', 'delete'.```"
            return self.response_message_whatsapp(msg)

        if body_split[0] in ['set', 'get']:
            get_partner = request.env['res.partner'].sudo().search([('ref', '=', body_split[1])])
            if not get_partner:
                msg = "```User is not exist.```"
                return self.response_message_whatsapp(msg)

            if from_whatsapp_number != get_partner.mobile:
                msg = "```Wrong user, the sender message must have same mobile number as user mobile number.```"
                return self.response_message_whatsapp(msg)
            
            if body_split[0] == 'set':
                return self.create_data(get_partner, body_split)
            elif body_split[0] == 'get':
                return self.get_data(get_partner, body_split)

        if body_split[0] in ['create', 'delete']:
            if body_split[0] == 'create':
                return self.create_new_user(body_split, from_whatsapp_number)
            elif body_split[0] == 'delete':
                return self.delete_user(body_split)

    def delete_user(self, body_split):
        if len(body_split) != 4:
            msg = "```Wrong format delete user, the sender message must send with this format: 'delete user <id_name> <password>'.```"
            return self.response_message_whatsapp(msg)

        user_id = request.env['res.users'].sudo().search([
            ('login', '=', body_split[2]),
            ('active', '=', True)
        ])
        if not user_id:
            msg = "```User is not exist.```"
            return self.response_message_whatsapp(msg)

        if user_id.partner_id.password_user != body_split[3]:
            msg = "```Wrong password.```"
            return self.response_message_whatsapp(msg)

        daily_finance_ids = request.env['daily.finance'].sudo().search([('partner_id', '=', user_id.partner_id.id)])
        for df in daily_finance_ids:
            df.unlink()

        report_finance_ids = request.env['finance.report'].sudo().search([('partner_id', '=', user_id.partner_id.id)])
        for rf in report_finance_ids:
            rf.unlink()

        user_id.active = False

        msg = "```Success archive user %s you can't no longer login into our system and all of your data will be deleted.```" % (user_id.login)
        return self.response_message_whatsapp(msg)

    def create_new_user(self, body_split, from_whatsapp_number):
        if len(body_split) != 5:
            msg = "```Wrong format create user, the sender message must send with this format: 'create user <id_name> <your_name> <password>'.```"
            return self.response_message_whatsapp(msg)

        existing_user_id = request.env['res.users'].sudo().search([('login', '=', body_split[2]), ('active', 'in', [False, True])])
        if existing_user_id:
            msg = "```%s as ID name already used.```" % (body_split[2])
            return self.response_message_whatsapp(msg)

        if existing_user_id:
            msg = "```%s as ID name already used.```" % (body_split[2])
            return self.response_message_whatsapp(msg)

        max_account = request.env['ir.config_parameter'].sudo().get_param('df.maximal_user')
        if not max_account:
            msg = "```Failed to create user, max account per phone number is not set on the system.```" % (body_split[2])
            return self.response_message_whatsapp(msg)

        total_user_by_phone = request.env['res.partner'].sudo().search([('mobile', '=', from_whatsapp_number)])
        if len(total_user_by_phone) > int(max_account) :
            msg = "```One number (%s) only can have %s users.```" % (from_whatsapp_number, max_account)
            return self.response_message_whatsapp(msg)

        user_id = request.env['res.users'].sudo().create({
            'name': body_split[3].replace("_", " "),
            'login': body_split[2],
            'password': body_split[4]
        })

        add_group_access = request.env.ref('daily_finance.group_daily_finance_user').sudo().write({
            'users': [(4, user_id.id)]
        })

        user_id.partner_id.write({
            'mobile': from_whatsapp_number,
            'ref': body_split[2],
            'password_user': body_split[4]
        })
        
        msg = "```Success create new user, login: %s | password: %s```" % (user_id.login, body_split[4])
        return self.response_message_whatsapp(msg)

    def message_rules(self):
        result = "Rules: " \
        "\n*CREATE*" \
        "\nvalue of <id_name> is your username/id_login in the system" \
        "\nvalue of <name> is your complete name, fill it like email no space" \
        "\nvalue of <password> is your user password" \
        "\n*Format message:*" \
        "\ncreate user <id_name> <name> <password>" \
        "\nexample: " \
        "\n*create user rehan123 Fahmi_Roihanul_Firdaus passwordku123*\n" \
        "\n*DELETE*" \
        "\nvalue of <id_name> is your username/id_login in the system" \
        "\nvalue of <password> is your user password" \
        "\n*Format message:*" \
        "\ndelete user <id_name> <password>" \
        "\nexample: " \
        "\n*delete user rehan123 passwordku123*\n" \
        "\n*SET*" \
        "\nvalue of <id_name> is your username/id_login in the system" \
        "\nvalue of <type> is 'income' or 'outcome'" \
        "\nvalue of <total_amount> is nominal of your amount example: 2.000.000" \
        "\nvalue of <usage> is ['food', 'salary', 'entertain', 'bill', 'other']" \
        "\nvalue of <date> is in format 'YYYY-mm-dd'" \
        "\n*Format message:*" \
        "\nset <name> <type> <total_amount> <usage>" \
        "\nOR" \
        "\nset <name> <type> <total_amount> <usage> <date>" \
        "\nexample: " \
        "\n*set rehan1 income 100.000.000 salary*" \
        "\nOR" \
        "\n*set rehan1 income 100.000.000 salary 2021-08-17*\n" \
        "\n*GET*" \
        "\nvalue of <id_name> is your username/id login in the system" \
        "\nvalue of <date_start> is in format 'YYYY-mm-dd'" \
        "\nvalue of <date_end> is in format 'YYYY-mm-dd'" \
        "\n*Format message:*" \
        "\nget <name> report <date_start> <date_end>" \
        "\nOR" \
        "\nget <id_name> report all>" \
        "\nexample: " \
        "\n*get rehan1 report 2021-08-17 2021-09-17*" \
        "\nOR" \
        "\n*get rehan1 report all*"

        return result

    def get_data(self, get_partner, body_split):
        all_total_income = 0
        all_total_outcome = 0
        total_income = 0
        total_outcome = 0

        if len(body_split) not in [5, 4]:
            msg = self.common_msg
            return self.response_message_whatsapp(msg)

        get_all_finance = request.env['daily.finance'].sudo().search([
            ('partner_id', '=', get_partner.id)
        ])

        all_income_data = get_all_finance.filtered(lambda x: x.type == 'income')
        if all_income_data:
            all_total_income = sum(data.total for data in all_income_data)

        all_outcome_data = get_all_finance.filtered(lambda x: x.type == 'outcome')
        if all_outcome_data:
            all_total_outcome = sum(data.total for data in all_outcome_data)
        
        all_total_balance = all_total_income - all_total_outcome

        if len(body_split) == 5:
            get_finance = request.env['daily.finance'].sudo().search([
                ('partner_id', '=', get_partner.id), 
                ('date', '>=', body_split[3]), 
                ('date', '<=', body_split[4])
            ])
            
            income_data = get_finance.filtered(lambda x: x.type == 'income')
            if income_data:
                total_income = sum(data.total for data in income_data)

            outcome_data = get_finance.filtered(lambda x: x.type == 'outcome')
            if outcome_data:
                total_outcome = sum(data.total for data in outcome_data)
            
            total_balance = total_income - total_outcome

            msg = "```Balance Movement:\n%s/%s\n\n" \
            "Sub Total Income: Rp %s\n" \
            "Sub Total Outcome: Rp %s\n" \
            "Sub Total Balance: Rp %s\n\n" \
            "Total Balance: Rp %s```" % (
                body_split[3], 
                body_split[4],
                f'{total_income:,}',
                f'{total_outcome:,}',
                f'{total_balance:,}',
                f'{all_total_balance:,}'
            )

            if body_split[2] == 'report_pdf':
                res = {
                    'partner_id': get_partner.id,
                    'select_all': False,
                    'start_date': body_split[3],
                    'end_date': body_split[4]
                }
                created, err = self.send_report_pdf(get_partner, res)
                if not created:
                    return err

            return self.response_message_whatsapp(msg)

        if body_split[3] == "all":
            msg = "```Balance Movement: \n\n" \
            "Total Income: Rp %s\n" \
            "Total Outcome: Rp %s\n\n" \
            "Total Balance: Rp %s```" % (
                f'{all_total_income:,}',
                f'{all_total_outcome:,}',
                f'{all_total_balance:,}'
            )

            if body_split[2] == 'report_pdf':
                res = {
                    'partner_id': get_partner.id,
                    'select_all': True
                }
                created, err = self.send_report_pdf(get_partner, res)
                if not created:
                    return err
                
            return self.response_message_whatsapp(msg)
        else:
            msg = self.common_msg
            return self.response_message_whatsapp(msg)

    def send_report_pdf(self, get_partner, res):
        account_sid = request.env['ir.config_parameter'].sudo().get_param('twilio.account_sid_finance')
        auth_token = request.env['ir.config_parameter'].sudo().get_param('twilio.auth_token_finance')
        from_number = request.env['ir.config_parameter'].sudo().get_param('twilio.mobile_finance')
        to_number = get_partner.mobile

        if not account_sid:
            msg = "Twilio Account SID is empty, please check it on settings"
            return False, self.response_message_whatsapp(msg)

        if not auth_token:
            msg = "Twilio Auth Token is empty, please check it on settings"
            return False, self.response_message_whatsapp(msg)

        if not from_number:
            msg = "Twilio Mobile Number is empty, please check it on settings"
            return False, self.response_message_whatsapp(msg)
        
        if not to_number:
            msg = "Mobile Phone is not exist on %s" % (get_partner.name)
            return False, self.response_message_whatsapp(msg)

        try:
            create_report_wizard = request.env['finance.report.wizard'].sudo().create(res)

            create_report_id = create_report_wizard.create_report()
            client = Client(account_sid, auth_token)
            from_whatsapp_number = 'whatsapp:%s' % (from_number)
            to_whatsapp_number = 'whatsapp:%s' % (to_number)
            media_url = self.generate_pdf_url(create_report_id)
            client_message = {
                "from_": from_whatsapp_number,
                "to": to_whatsapp_number,
                "media_url": media_url
            }

            client.messages.create(**client_message)
            return True, create_report_id
        except Exception as e:
            msg = "Failed to send PDF, %s " % (str(e))
            return False, self.response_message_whatsapp(msg)

    def generate_pdf_url(self, report_id):
        finance_report_id = request.env['finance.report'].sudo().browse(report_id)
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        report_ref = 'daily_finance.finance_pdf_report'
        raport_pdf_name = "Report_Finance_%s" % (finance_report_id.partner_id.name)
        return "%s/api/v1/%s/%s/%s" % (
            base_url,
            report_ref, 
            report_id, 
            raport_pdf_name
        )

    @http.route('/api/v1/<report_ref>/<int:id>/<raport_name>', type='http', auth="public", website=True, sitemap=False)
    def raport_pdf_file(self, report_ref=None, id=0, **kw):
        if report_ref and id:
            pdf = request.env.ref(report_ref).sudo()._render_qweb_pdf([id])[0]
            return self.return_web_pdf_view(pdf)

    def return_web_pdf_view(self, pdf=None):
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)
        
    def create_data(self, get_partner, body_split):
        if len(body_split) not in [5, 6]:
            msg = self.common_msg
            return self.response_message_whatsapp(msg)
            
        if body_split[2] not in ['income', 'outcome']:
            msg = "```Wrong type, type value must in 'income' or 'outcome'.```"
            return self.response_message_whatsapp(msg)
                    
        try:
            amount_total = float(body_split[3].replace(".", ""))
        except Exception as e:
            msg = "```Wrong amount format, %s```" % (e)
            return self.response_message_whatsapp(msg)
            
        if body_split[4] not in ['food', 'salary', 'entertain', 'bill', 'other']:
            msg = "```Wrong usage type, must in 'food', 'salary', 'entertain', 'bill', 'other'.```"
            return self.response_message_whatsapp(msg)

        res = {
            'partner_id': get_partner.id,
            'type': body_split[2],
            'total': float(body_split[3].replace('.', '')),
            'usage': body_split[4]
        }

        if len(body_split) == 6:
            res['date'] = body_split[5]

        create_daily_finance = request.env['daily.finance'].sudo().create(res)

        msg = "```Successfully create data finance: %s```" % (
            create_daily_finance.display_name
        )
        return self.response_message_whatsapp(msg)

    def response_message_whatsapp(self, msg):
        resp = MessagingResponse()
        resp.message(msg)
        return str(resp)
