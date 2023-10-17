# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


# inherit the product.product object
class ProductProduct(models.Model):
    _inherit = "product.product"
