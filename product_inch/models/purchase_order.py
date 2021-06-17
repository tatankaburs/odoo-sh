# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    lumber_inch = fields.Float(string = 'PM')
    m3_piece = fields.Float(string = 'M3T', help="Metros Cúbicos de Trozo")
    metric_volum = fields.Float(string = 'M3M', help="Metros Cúbicos de Madera")
    product_qty = fields.Float(string='Cantidad')
    orchard_id = fields.Many2one('res.partner', string = 'Fundo')
    code_fsc_id = fields.Many2one('res.partner.fsc', string ='Código FSC',  domain="[('partner_id', '=', partner_id)]" )
    category_id = fields.Many2many(related='partner_id.category_id', string='Categorias')
    type_fsc = fields.Selection([
        ("fsc_100", "FSC 100%"), 
        ("fsc_mix", "FSC Mixto"),
        ("fsc_wood_controler", "Madera Controlada FSC"),
        ("wood_controler", "Madera Controlada"),
    ], string="Categoría Proveedor")

    
    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s", self.partner_id.name))
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'user_id': False,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
            'orchard_id': self.orchard_id.id,
        }
       
    @api.model
    def create(self, vals):
        reg = super(PurchaseOrder, self).create(vals)
        lumber_inch = 0
        m3_piece = 0
        metric_volum = 0
        product_qty = 0
        
        for item in reg.order_line:
            lumber_inch += item.lumber_inch
            m3_piece += item.m3_piece
            metric_volum += item.metric_volum
            product_qty += item.product_qty
        
        reg.lumber_inch = lumber_inch
        reg.m3_piece = m3_piece
        reg.metric_volum = metric_volum
        reg.product_qty = product_qty
        
        return reg

    def write(self, vals):
        super(PurchaseOrder, self).write(vals)
        lumber_inch = 0
        m3_piece = 0
        metric_volum = 0
        product_qty = 0
        
        for item in self.order_line:
            lumber_inch += item.lumber_inch
            m3_piece += item.m3_piece
            metric_volum += item.metric_volum
            product_qty += item.product_qty
        
        values = {}
        values['lumber_inch'] = lumber_inch
        values['m3_piece'] = m3_piece
        values['metric_volum'] = metric_volum
        values['product_qty'] = product_qty
              
        return super(PurchaseOrder, self).write(values)