# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Stock Picking Type Access',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'description': """ Mejora permisos en vista de transacciones entre bodegas""",
    'author': 'Iván Masías - ivan.masias.ortiz@gmail.com',
    'depends': ['stock'],
    'data': [
        #'views/res_partner.xml',
        'views/stock_picking.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
