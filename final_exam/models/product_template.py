# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


# inherit product.template object
class ProductTemplate(models.Model):
    _inherit = "product.template"

    # add a new as per requirement
    sequence = fields.Integer(string="Sequence")
