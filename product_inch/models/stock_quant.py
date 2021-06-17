# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from psycopg2 import OperationalError

class StockQuant(models.Model):
    _inherit = "stock.quant"
    
    def _multi_qt_lumber_inch(self):
        for rec in self:
            rec.lumber_inch = rec.product_id.lumber_inch * rec.quantity
    
    def _multi_qt_m3_piece(self):
        for rec in self:
            rec.m3_piece = rec.product_id.m3_piece * rec.quantity
    
    def _multi_qt_metric_volum(self):
        for rec in self:
            rec.metric_volum = rec.product_id.metric_volum * rec.quantity
    
    lumber_inch = fields.Float(compute='_multi_qt_lumber_inch', string = 'PM', store=True)
    m3_piece = fields.Float(string = 'M3T', compute='_multi_qt_m3_piece', help="Metros Cúbicos de Trozo", store=True)
    metric_volum = fields.Float(string = 'M3M', compute='_multi_qt_metric_volum', help="Metros Cúbicos de Madera", store=True)
    
    @api.model
    def _update_available_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, in_date=None):
        """ Increase or decrease `reserved_quantity` of a set of quants for a given set of
        product_id/location_id/lot_id/package_id/owner_id.

        :param product_id:
        :param location_id:
        :param quantity:
        :param lot_id:
        :param package_id:
        :param owner_id:
        :param datetime in_date: Should only be passed when calls to this method are done in
                                 order to move a quant. When creating a tracked quant, the
                                 current datetime will be used.
        :return: tuple (available_quantity, in_date as a datetime)
        """
        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True)
        if lot_id and quantity > 0:
            quants = quants.filtered(lambda q: q.lot_id)

        incoming_dates = [d for d in quants.mapped('in_date') if d]
        incoming_dates = [fields.Datetime.from_string(incoming_date) for incoming_date in incoming_dates]
        if in_date:
            incoming_dates += [in_date]
        # If multiple incoming dates are available for a given lot_id/package_id/owner_id, we
        # consider only the oldest one as being relevant.
        if incoming_dates:
            in_date = fields.Datetime.to_string(min(incoming_dates))
        else:
            in_date = fields.Datetime.now()

        for quant in quants:
            try:
                with self._cr.savepoint(flush=False):  # Avoid flush compute store of package
                    self._cr.execute("SELECT 1 FROM stock_quant WHERE id = %s FOR UPDATE NOWAIT", [quant.id], log_exceptions=False)
                    quant.write({
                        'quantity': quant.quantity + quantity,
                        'in_date': in_date,
                    })
                    break
            except OperationalError as e:
                if e.pgcode == '55P03':  # could not obtain the lock
                    continue
                else:
                    # Because savepoint doesn't flush, we need to invalidate the cache
                    # when there is a error raise from the write (other than lock-error)
                    self.clear_caches()
                    raise
        else:
            production_id = self.env['mrp.production'].search([('lot_producing_id', '=', lot_id.id),])
            if production_id.id:
                lumber_inch = 0
                m3_piece = 0
                metric_volum = 0
                for item in production_id.move_raw_ids:
                    lumber_inch += item.lumber_inch
                    m3_piece += item.m3_piece
                    metric_volum += item.metric_volum
            self.create({
                'product_id': product_id.id,
                'location_id': location_id.id,
                'lumber_inch': lumber_inch,
                'm3_piece': m3_piece,
                'metric_volum': metric_volum,
                'quantity': quantity,
                'lot_id': lot_id and lot_id.id,
                'package_id': package_id and package_id.id,
                'owner_id': owner_id and owner_id.id,
                'in_date': in_date,
            })
        return self._get_available_quantity(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=False, allow_negative=True), fields.Datetime.from_string(in_date)
