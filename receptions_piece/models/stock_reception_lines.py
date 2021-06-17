# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class StockReceptionLines(models.Model):
    _name = 'stock.reception.lines'
    _description = 'Stock Reception Lines'
    
    name = fields.Many2one('product.product', string='Producto', required=True)
    banks_id =  fields.Many2one('stock.bank', string='Banco')
    quantity = fields.Float(string='Cantidad')
    reception_id = fields.Many2one('stock.reception', string='Recepciones')
    