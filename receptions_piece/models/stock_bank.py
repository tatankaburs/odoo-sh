# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class StockBank(models.Model):
    _name = 'stock.bank'
    
    name = fields.Char(string='Nombre', required=True)
