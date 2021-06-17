# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    lumber_inch = fields.Float(string = 'PM')
    m3_piece = fields.Float(string = 'M3T', help="Metros Cúbicos de Trozo")
    metric_volum = fields.Float(string = 'M3M', help="Metros Cúbicos de Madera")
    product_uom_qty = fields.Float(string = 'Cant. Piezas')
    
    @api.onchange('bom_id', 'product_id', 'product_qty', 'product_uom_id')
    def _onchange_move_raw(self):
        if not self.bom_id and not self._origin.product_id:
            return
        # Clear move raws if we are changing the product. In case of creation (self._origin is empty),
        # we need to avoid keeping incorrect lines, so clearing is necessary too.
        if self.product_id != self._origin.product_id:
            self.move_raw_ids = [(5,)]
        if self.bom_id and self.product_qty > 0:
            # keep manual entries
            list_move_raw = [(4, move.id) for move in self.move_raw_ids.filtered(lambda m: not m.bom_line_id)]
            moves_raw_values = self._get_moves_raw_values()
            move_raw_dict = {move.bom_line_id.id: move for move in self.move_raw_ids.filtered(lambda m: m.bom_line_id)}
            for move_raw_values in moves_raw_values:
                
                #Agrega medidas madereras
                product_id = self.env['product.product'].browse(moves_raw_values[0]['product_id'])
                # add new entries
                if product_id.type_measure == 'lumber_inch':
                    move_raw_values['lumber_inch'] = product_id.lumber_inch * move_raw_values['product_uom_qty']
                elif product_id.type_measure == 'm3_piece':
                    move_raw_values['m3_piece'] = product_id.m3_piece * move_raw_values['product_uom_qty']
                elif product_id.type_measure == 'metric_volum':
                    move_raw_values['metric_volum'] = product_id.metric_volum * move_raw_values['product_uom_qty']
                
                if move_raw_values['bom_line_id'] in move_raw_dict:
                    # update existing entries
                    list_move_raw += [(1, move_raw_dict[move_raw_values['bom_line_id']].id, move_raw_values)]
                else:
                    list_move_raw += [(0, 0, move_raw_values)]
            self.move_raw_ids = list_move_raw
        else:
            self.move_raw_ids = [(2, move.id) for move in self.move_raw_ids.filtered(lambda m: m.bom_line_id)]
    
    @api.model
    def create(self, vals):
        reg = super(MrpProduction, self).create(vals)
        lumber_inch = 0
        m3_piece = 0
        metric_volum = 0
        product_uom_qty = 0
        
        for item in reg.move_raw_ids:
            lumber_inch += item.lumber_inch
            m3_piece += item.m3_piece
            metric_volum += item.metric_volum
            product_uom_qty += item.product_uom_qty
        
        reg.lumber_inch = lumber_inch
        reg.m3_piece = m3_piece
        reg.metric_volum = metric_volum
        reg.product_uom_qty = product_uom_qty
        
        return reg

    def write(self, vals):
        super(MrpProduction, self).write(vals)
        lumber_inch = 0
        m3_piece = 0
        metric_volum = 0
        product_uom_qty = 0
        
        for item in self.move_raw_ids:
            lumber_inch += item.lumber_inch
            m3_piece += item.m3_piece
            metric_volum += item.metric_volum
            product_uom_qty += item.product_uom_qty
        
        values = {}
        values['lumber_inch'] = lumber_inch
        values['m3_piece'] = m3_piece
        values['metric_volum'] = metric_volum
        values['product_uom_qty'] = product_uom_qty
              
        return super(MrpProduction, self).write(values)