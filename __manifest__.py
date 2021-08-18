# -*- coding: utf-8 -*-
{
    'name': 'Daily Finance',
    "license": "LGPL-3",
    'summary': """
        Daily Finance
        """,
    'description': """
        Daily Finance Income and Outcome
    """,
    'images': ['static/description/icon.png'],
    'author': "Rehan | Fahmi Roihanul Firdaus",
    'website': "https://www.frayhands.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'mail', 'code_backend_theme'],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/daily_finance_views.xml',
        'views/daily_finance_config_views.xml',
        'views/finance_report_views.xml',
        'views/report_finance.xml',
        'views/report.xml',
        'wizard/finance_report_wizard_views.xml',
        'views/finance_menu.xml',
    ]
}