# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

class StockMove(models.Model):
    _inherit = "stock.move"
    
    lumber_inch = fields.Float(string = 'PM')
    m3_piece = fields.Float(string = 'M3T', help="Metros Cúbicos de Trozo")
    metric_volum = fields.Float(string = 'M3M', help="Metros Cúbicos de Madera")
    
    @api.onchange('product_uom_qty')
    def _onchange_lumber_inch(self):
        if self.product_id.type_measure == 'lumber_inch':
            self.lumber_inch = self.product_id.lumber_inch * self.product_uom_qty
    
    @api.onchange('product_uom_qty')
    def _onchange_m3_piece(self):
        if self.product_id.type_measure == 'm3_piece':
            self.m3_piece = self.product_id.m3_piece * self.product_uom_qty
    
    @api.onchange('product_uom_qty')
    def _onchange_metric_volum(self):
        if self.product_id.type_measure == 'metric_volum':
            self.metric_volum = self.product_id.metric_volum * self.product_uom_qty