# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'
    
    partner_id = fields.Many2one(related='warehouse_id.partner_id', string='Empresa')
    
    
