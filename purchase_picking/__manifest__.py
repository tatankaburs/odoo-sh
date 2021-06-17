# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase in Picking',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'description': """ Mejora la vista de compras, cambia donde mostrar el origen de entrega de productos""",
    'author': 'Iván Masías - ivan.masias.ortiz@gmail.com',
    'depends': ['stock','stock_picking_type_access'],
    'data': [
        'views/purchase_order.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
