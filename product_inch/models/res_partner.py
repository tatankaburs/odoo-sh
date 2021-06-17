# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields
from odoo.fields import Many2one

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    type = fields.Selection(selection_add=[
        ('ranch','Fundos')
    ], string='Tipo')
    
    code_sfc_ids = fields.One2many('res.partner.fsc', 'partner_id', string="Código FSC")    
    
    def _get_contact_name(self, partner, name):
        return "%s" % (name)