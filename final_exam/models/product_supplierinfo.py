# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, _


# inherit product.supplierinfo object
class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    # add a new as per requirement
    sequence = fields.Integer(
        string="Sequence",
    )
