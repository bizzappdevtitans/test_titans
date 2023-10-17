# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


# inherit product.template object
class ProductTemplate(models.Model):
    _inherit = "product.template"

    # add a new as per requirement
    new_sequence = fields.Integer(string="Sequence")
