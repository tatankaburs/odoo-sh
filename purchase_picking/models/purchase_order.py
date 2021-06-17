# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    partner_id2 = fields.Many2one(related='picking_type_id.warehouse_id.partner_id', string='Empresa')
    
    
