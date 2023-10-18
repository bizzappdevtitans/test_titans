# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"


# inherit sale.order.line object
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    _description = "Sales Order Line"

    product_supplier_id = fields.Many2one(
        comodel_name="product.supplierinfo", string="vendor"
    )

    # this code is in progress
    # @api.model
    # def default_get(self, fields):
    #     """default_get method  #T00466"""
    #     vals = super(SaleOrderLine, self).default_get(fields)
    #     for vendors in self.product_supplier_id:
    #         if vendors.price_of_product == min(vendors.price_of_product):
    #             vals["product_supplier_id"] = vendors.partner_id.id
    #     return vals
