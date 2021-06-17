# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.tools.misc import get_lang
from dateutil.relativedelta import relativedelta

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    
    lumber_inch = fields.Float(string = 'PM')
    m3_piece = fields.Float(string = 'M3T', help="Metros Cúbicos de Trozo")
    metric_volum = fields.Float(string = 'M3M', help="Metros Cúbicos de Madera")
    type_measure = fields.Selection(related='product_id.type_measure', string='Medida Maderera', readonly=True, store=True)
    
    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            
            product_uom_qty = 0
            
            if line.product_id.type_measure == 'lumber_inch':
                product_uom_qty = self.lumber_inch = line.product_id.lumber_inch * line.product_uom_qty
            elif line.product_id.type_measure == 'm3_piece':
                product_uom_qty = self.m3_piece = line.product_id.m3_piece * line.product_uom_qty
            elif line.product_id.type_measure == 'metric_volum':
                product_uom_qty = self.metric_volum = line.product_id.metric_volum * line.product_uom_qty
            else:
                product_uom_qty = line.product_uom_qty
            
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                product_uom_qty,
                vals['product'],
                vals['partner'],
                )
            
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
            'lumber_inch': self.product_id.lumber_inch * self.product_qty,
            'm3_piece': self.product_id.m3_piece * self.product_qty,
            'metric_volum': self.product_id.metric_volum * self.product_qty,
        }
    
    def _product_id_change(self):
        if not self.product_id:
            return

        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        product_lang = self.product_id.with_context(
            lang=get_lang(self.env, self.partner_id.lang).code,
            partner_id=self.partner_id.id,
            company_id=self.company_id.id,
        )
        self.name = self._get_product_purchase_description(product_lang)
        
        #Agrega pulgadas madereras
        self.lumber_inch = self.product_id.lumber_inch
        self.m3_piece = self.product_id.m3_piece
        self.metric_volum = self.product_id.metric_volum
        
        self._compute_tax_id()
        
    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        self.ensure_one()
        product = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)
        description_picking = product._get_description(self.order_id.picking_type_id)
        if self.product_description_variants:
            description_picking += self.product_description_variants
        date_planned = self.date_planned or self.order_id.date_planned
        return {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'date': date_planned,
            'date_deadline': date_planned + relativedelta(days=self.order_id.company_id.po_lead),
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': (self.orderpoint_id and not (self.move_ids | self.move_dest_ids)) and self.orderpoint_id.location_id.id or self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'description_picking': description_picking,
            'propagate_cancel': self.propagate_cancel,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom.id,
            'lumber_inch': self.lumber_inch,
            'm3_piece': self.m3_piece,
            'metric_volum': self.metric_volum,
        }
        
        
    
    