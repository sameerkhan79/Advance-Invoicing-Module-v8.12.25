# -*- coding: utf-8 -*-
{
    "name": "Invoice Product Attribute Wizard & CRM Service History",
    "version": "18.0.1.0.0",
    "sequence": -1000,
    "price": 300,
    "currency": "USD",
    "summary": "Direct invoice creation with product attributes, dynamic headers, and CRM service history tracking.",
    "description": """
Invoice Product Attribute Wizard & CRM Service History
======================================================

This module extends Odoo Accounting and CRM with the following features:

🔹 **Direct Invoice Creation**
- Create invoices directly in Accounting without going through sales quotations.
- Add products and configure attributes/variants in invoices, just like in Sale Orders.

🔹 **Dynamic Invoice Headers**
- Each invoice line has a checkbox to mark as part of the invoice header.
- Once confirmed, invoices display a dynamic/customized header.
- Easily email invoices to customers.

🔹 **CRM Customer Service History**
- Adds three new tabs under CRM customers.
- Maintain full history of services provided to each customer.
- Improve customer relationship tracking and after-sales support.

""",
    "author": "Muhammad Osama Nadeem",
    "website": "https://xynotech.com",
    "category": "Accounting/Invoicing",
    "license": "LGPL-3",
    "depends": [
        "base",
        "account",
        "crm",
        "contacts",
        "account_payment",
    ],
    "data": [
        "security/security_group.xml",
        "security/ir.model.access.csv",
        "views/account_move_lines.xml",
        "views/crm_inherit.xml",
        "views/crm_label.xml",
        "views/crm_copyright.xml",
        "views/crm_trademark_history.xml",
        "views/invoice_report_inherit.xml",
        "views/account_move_send_wizard_inherit.xml",
        'views/account_payment_wizard.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "account_move_inherit/static/src/**/*.js",
            "account_move_inherit/static/src/**/*.xml",
            "account_move_inherit/static/src/**/*.scss",
        ],
    },
    "images": [
        "static/description/icon.png",       
        # "static/description/cover.png",      
        "static/description/1.png",
        "static/description/2.png",
        "static/description/3.png",
        "static/description/4.png",
        "static/description/5.png",
        "static/description/6.png",
        "static/description/7.png",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
