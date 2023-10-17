# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


# inherit product.supplierinfo object
class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    # add a new as per requirement
    new_sequence = fields.Integer(
        string="Sequence",
    )
