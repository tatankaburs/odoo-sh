# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    type_measure = fields.Selection([
        ("lumber_inch", "Pulgada Maderera"), 
        ("m3_piece", "M3 Trozo"),
        ("metric_volum", "Volumen Metrico"),
    ], string="Medida Maderera")

    bom_id = fields.Many2one('mrp.bom', string = 'Lista de Materiales')
    
    @api.onchange('density1', 'width1', 'long1')
    def _onchange_lumber_inch_calc(self):
        if self.density1 != 0 and self.width1 != 0 and self.long1 != 0:
            self.lumber_inch = self.density1 * (self.width1/10) * (self.long1/3.2)
        else:
            self.lumber_inch = 0.0
                
    @api.onchange('diameter', 'length')
    def _onchange_m3_piece_calc(self):
        if self.diameter != 0 and self.length != 0:
            self.m3_piece = (self.diameter ** 2) * (self.length/10000)
        else:
            self.m3_piece = 0.0
                
    @api.onchange('density2', 'width2', 'long2')
    def _onchange_metric_volum_calc(self):
        if self.density2 != 0 and self.width2 != 0 and self.long2 != 0:
            self.metric_volum = (self.density2 * self.width2 * self.long2)/10**6
        else:
            self.metric_volum = 0.0
    
    density1 = fields.Float(string = 'Espesor', default=0.0)
    width1 = fields.Float(string = 'Ancho', default=0.0)
    long1 = fields.Float(string = 'Largo', default=0.0)
    lumber_inch = fields.Float(string = 'Pulgada Maderera')
    
    diameter = fields.Float(string = 'Diametro', default=0.0)
    length = fields.Float(string = 'Longitud', default=0.0)
    m3_piece = fields.Float(string = 'M3 Trozo')
    
    density2 = fields.Float(string = 'Espesor', default=0.0)
    width2 = fields.Float(string = 'Ancho', default=0.0)
    long2 = fields.Float(string = 'Largo', default=0.0)
    metric_volum = fields.Float(string = 'Volumen Metrico')
    
    
    