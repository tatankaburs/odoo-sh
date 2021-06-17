# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class ResPartnerFsc(models.Model):
    _name= "res.partner.fsc"
    _description = "Res Partner Fsc"
    
    name = fields.Char(string='Código FSC', required=True)
    partner_id = fields.Many2one('res.partner', string='Clientes')
