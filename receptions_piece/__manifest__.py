# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Receptions Pieces',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'description': """ Recepción de trozos a la llegada de camiones""",
    'author': 'Iván Masías - ivan.masias.ortiz@gmail.com',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_sequence.xml',
        'views/stock_reception.xml',
        'views/stock_bank.xml',
        'views/stock_reception_menu.xml',
        'views/web_asset_backend_template.xml',
    ],
    'qweb': [
        'static/src/xml/stock_reception_tablet.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
