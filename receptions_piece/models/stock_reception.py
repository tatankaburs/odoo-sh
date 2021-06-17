# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase

class StockReception(models.Model):
    _name = 'stock.reception'
    _description = 'Stock Reception'
    
    @api.model
    def _default_picking_type(self):
        return self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)
    
    name = fields.Char(string='Nombre', default=lambda self: self.env['ir.sequence'].next_by_code('stock.reception'), readonly=True)
    reception_date = fields.Datetime(string='Fecha Recepción')
    partner_id = fields.Many2one('res.partner', string='Proveedor')
    user_id = fields.Many2one('res.users', string='Recepciona', default=lambda self: self.env.user.id)
    picking_type_id = fields.Many2one('stock.picking.type', string='Origen', states=Purchase.READONLY_STATES, required=True, default=_default_picking_type, domain="['|', ('warehouse_id', '=', False), ('warehouse_id.company_id', '=', company_id)]",
        help="This will determine operation type of incoming shipment")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    orders_id = fields.Many2one('purchase.order', string='Presupuesto')
    notes = fields.Text('Notas')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('received','Recibido'),
        ('validated','Validado'),
        ],string='Estado', default='draft')
    
    reception_lines = fields.One2many('stock.reception.lines', 'reception_id', 'Agregar Trozo', required=False)
    
    @api.model
    def _get_picking_type(self, company_id):
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return picking_type[:1]
    
    def action_draft(self):
        self.state = 'draft'
    
    def action_received(self):
        self.state = 'received'

    def action_validated(self):
        self.state = 'validated'
    
    def action_purchase_order(self):
        obj_crm_lead = self.env['purchase.order']
        data = []
        values = {'order_line': list()}
        order = {
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id.id,
            'date_planned': self.reception_date,
            'order_line': list(),
            #'partner_ref': 
            #'date_planned':
            }

        for line in self.reception_lines:
            data.append((0,0, {
                'product_id' : line.name.id,
                'product_qty': line.quantity,

            }))
            
        order['order_line'].extend(data)
        res = obj_crm_lead.create(order)
        self.orders_id = res.id

    
    