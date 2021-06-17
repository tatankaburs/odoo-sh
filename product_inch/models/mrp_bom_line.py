# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    lumber_inch = fields.Float(string = 'PM')
    m3_piece = fields.Float(string = 'M3T', help="Metros Cúbicos de Trozo")
    metric_volum = fields.Float(string = 'M3M', help="Metros Cúbicos de Madera")
    
    @api.onchange('product_id', 'product_qty')
    def _onchange_move_raw(self):
        if self.product_id:
            if self.product_id.type_measure == 'lumber_inch':
                self.lumber_inch = self.product_id.lumber_inch * self.product_qty
            elif self.product_id.type_measure == 'm3_piece':
                self.m3_piece = self.product_id.m3_piece * self.product_qty
            elif self.product_id.type_measure == 'metric_volum':
                self.metric_volum = self.product_id.metric_volum * self.product_qty
                
                