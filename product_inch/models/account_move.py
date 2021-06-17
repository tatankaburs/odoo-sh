# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import copy

from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _move_autocomplete_invoice_lines_create(self, vals_list):
        ''' During the create of an account.move with only 'invoice_line_ids' set and not 'line_ids', this method is called
        to auto compute accounting lines of the invoice. In that case, accounts will be retrieved and taxes, cash rounding
        and payment terms will be computed. At the end, the values will contains all accounting lines in 'line_ids'
        and the moves should be balanced.

        :param vals_list:   The list of values passed to the 'create' method.
        :return:            Modified list of values.
        '''
        
        new_vals_list = []

        vals_inch = copy.deepcopy(vals_list[0]['invoice_line_ids'])

        for vals in vals_list:
            vals = dict(vals)

            if vals.get('invoice_date') and not vals.get('date'):
                vals['date'] = vals['invoice_date']

            default_move_type = vals.get('move_type') or self._context.get('default_move_type')
            ctx_vals = {}
            if default_move_type:
                ctx_vals['default_move_type'] = default_move_type
            if vals.get('journal_id'):
                ctx_vals['default_journal_id'] = vals['journal_id']
                # reorder the companies in the context so that the company of the journal
                # (which will be the company of the move) is the main one, ensuring all
                # property fields are read with the correct company
                journal_company = self.env['account.journal'].browse(vals['journal_id']).company_id
                allowed_companies = self._context.get('allowed_company_ids', journal_company.ids)
                reordered_companies = sorted(allowed_companies, key=lambda cid: cid != journal_company.id)
                ctx_vals['allowed_company_ids'] = reordered_companies
            self_ctx = self.with_context(**ctx_vals)
            vals = self_ctx._add_missing_default_values(vals)

            is_invoice = vals.get('move_type') in self.get_invoice_types(include_receipts=True)

            if 'line_ids' in vals:
                vals.pop('invoice_line_ids', None)
                new_vals_list.append(vals)
                continue

            if is_invoice and 'invoice_line_ids' in vals:
                vals['line_ids'] = vals['invoice_line_ids']

            vals.pop('invoice_line_ids', None)

            move = self_ctx.new(vals)
            new_vals_list.append(move._move_autocomplete_invoice_lines_values())
    
        for item in new_vals_list[0]['line_ids']:
            for reg in vals_inch:
                if reg[1] == item[1]:
                    if 'lumber_inch' in reg[2]:
                        item[2]['type_measure'] = 'lumber_inch'
                        item[2]['lumber_inch'] = reg[2]['lumber_inch']
                        item[2]['m3_piece'] = 0.0
                        item[2]['metric_volum'] = 0.0
                    if 'm3_piece' in reg[2]:
                        item[2]['type_measure'] = 'm3_piece'
                        item[2]['lumber_inch'] = 0.0
                        item[2]['m3_piece'] = reg[2]['m3_piece']
                        item[2]['metric_volum'] = 0.0
                    if 'metric_volum' in reg[2]:
                        item[2]['type_measure'] = 'metric_volum'
                        item[2]['lumber_inch'] = 0.0
                        item[2]['m3_piece'] = 0.0
                        item[2]['metric_volum'] = reg[2]['metric_volum']

        return new_vals_list