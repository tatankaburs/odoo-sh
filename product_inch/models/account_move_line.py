# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    lumber_inch = fields.Float(string = 'PM')
    m3_piece = fields.Float(string = 'M3T', help="Metros Cúbicos de Trozo")
    metric_volum = fields.Float(string = 'M3M', help="Metros Cúbicos de Madera")
    type_measure = fields.Selection(related='product_id.type_measure', string='Medida Maderera', readonly=True, store=True)

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):

        #type_measure,lumber_inch, m3_piece, metric_volum

        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}
        
        if self.type_measure == 'lumber_inch':
            self.lumber_inch = product.lumber_inch * quantity
            quantity = self.lumber_inch
        elif self.type_measure == 'm3_piece':
            self.m3_piece = product.m3_piece * quantity
            quantity = self.m3_piece
        elif self.type_measure == 'metric_volum':
            self.metric_volum = product.metric_volum * quantity
            quantity = self.metric_volum

        # Compute 'price_subtotal'.
        line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * line_discount_price_unit

        # Compute 'price_total'.
        if taxes:
            taxes_res = taxes._origin.compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        #In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res
