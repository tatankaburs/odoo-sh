# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime, time
from psycopg2 import OperationalError
from odoo import models, registry, SUPERUSER_ID
from odoo.tools import float_compare, split_every
from odoo.addons.stock.models.stock_rule import ProcurementException

_logger = logging.getLogger(__name__)

class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'
    
def _procure_orderpoint_confirm(self, use_new_cursor=False, company_id=None, raise_user_error=True):
        """ Create procurements based on orderpoints.
        :param bool use_new_cursor: if set, use a dedicated cursor and auto-commit after processing
            1000 orderpoints.
            This is appropriate for batch jobs only.
        """
        self = self.with_company(company_id)
        orderpoints_noprefetch = self.read(['id'])
        orderpoints_noprefetch = [orderpoint['id'] for orderpoint in orderpoints_noprefetch]

        for orderpoints_batch in split_every(1000, orderpoints_noprefetch):
            if use_new_cursor:
                cr = registry(self._cr.dbname).cursor()
                self = self.with_env(self.env(cr=cr))
            orderpoints_batch = self.env['stock.warehouse.orderpoint'].browse(orderpoints_batch)
            orderpoints_exceptions = []
            while orderpoints_batch:
                procurements = []
                for orderpoint in orderpoints_batch:
                    if float_compare(orderpoint.qty_to_order, 0.0, precision_rounding=orderpoint.product_uom.rounding) == 1:
                        date = datetime.combine(orderpoint.lead_days_date, time.min)
                        values = orderpoint._prepare_procurement_values(date=date)
                        procurements.append(self.env['procurement.group'].Procurement(
                            orderpoint.product_id, orderpoint.qty_to_order, orderpoint.product_uom,
                            orderpoint.location_id, orderpoint.name, orderpoint.name,
                            orderpoint.company_id, orderpoint.product_id.lumber_inch, orderpoint.product_id.m3_piece, orderpoint.product_id.metric_volum, values))

                try:
                    with self.env.cr.savepoint():
                        self.env['procurement.group'].with_context(from_orderpoint=True).run(procurements, raise_user_error=raise_user_error)
                except ProcurementException as errors:
                    for procurement, error_msg in errors.procurement_exceptions:
                        orderpoints_exceptions += [(procurement.values.get('orderpoint_id'), error_msg)]
                    failed_orderpoints = self.env['stock.warehouse.orderpoint'].concat(*[o[0] for o in orderpoints_exceptions])
                    if not failed_orderpoints:
                        _logger.error('Unable to process orderpoints')
                        break
                    orderpoints_batch -= failed_orderpoints

                except OperationalError:
                    if use_new_cursor:
                        cr.rollback()
                        continue
                    else:
                        raise
                else:
                    orderpoints_batch._post_process_scheduler()
                    break

            # Log an activity on product template for failed orderpoints.
            for orderpoint, error_msg in orderpoints_exceptions:
                existing_activity = self.env['mail.activity'].search([
                    ('res_id', '=', orderpoint.product_id.product_tmpl_id.id),
                    ('res_model_id', '=', self.env.ref('product.model_product_template').id),
                    ('note', '=', error_msg)])
                if not existing_activity:
                    orderpoint.product_id.product_tmpl_id.activity_schedule(
                        'mail.mail_activity_data_warning',
                        note=error_msg,
                        user_id=orderpoint.product_id.responsible_id.id or SUPERUSER_ID,
                    )

            if use_new_cursor:
                cr.commit()
                cr.close()

        return {}