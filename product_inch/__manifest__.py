# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Inch',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'description': """ Calculos pulgada maderera""",
    'author': 'Iván Masías - ivan.masias.ortiz@gmail.com',
    'depends': ['stock','purchase','product','procurement_jit','sale'],
    'data': [
        'report/purchase_order_templates.xml',
        'report/purchase_quotation_templates.xml',
        'security/ir.model.access.csv',
        'views/account_move_line.xml',
        'views/product_template.xml',
        'views/purchase_order.xml',
        'views/purchase_order_line.xml',
        'views/sale_order_line.xml',
        'views/stock_move.xml',
        'views/stock_quant.xml',
        'views/stock_picking.xml',
        'views/mrp_production.xml',
        'views/mrp_bom.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
