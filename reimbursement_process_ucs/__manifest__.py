# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Uncanny Consulting Services LLP
#    Copyright (C) 2023 Uncanny Consulting Services LLP (<https://uncannycs.com>).
#
##############################################################################
{
    'name': 'Reimbursement Process UCS',
    "version": "17.0.1.0.0",
    "website": "https://uncannycs.com",
    "author": "Uncanny Consulting Services LLP",
    "maintainers": "Uncanny Consulting Services LLP",
    "license": "Other proprietary",
    "category": "Human Resources",
    "summary": "This module is designed to manage and approve the reimbursement process.",
    "depends": [
        'hr_expense','mail','account','base','hr_contract' ,'hr_payroll'
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        # "views/reimbursement_head_views.xml",
        "views/reimbursement_views.xml",
        "reports/reimbursement_report.xml",
        "views/reimbursement_report.xml",
        "views/hr_payslip_views.xml",
        "views/menuitem.xml",
        "wizard/reimbursement_reason_wizard_views.xml"
    ],

    "installable": True,
    "application": False,
    "images": ["static/description/icon.png"],
}
