# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models


# inherit sale.order.line object
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    _description = "Sales Order Line"

    # add a new Many2one field into a sale order line
    # product_supplier_id = Many2one(
    #     comodel_name="product.supplierinfo",
    #     string="Product Supplier",
    #     ondelete="cascade",
    #     copy=False,
    # )
    product_supplier_id = fields.Many2one(
        comodel_name="product.supplierinfo", string="vendor"
    )

    @api.model
    def default_get(self, fields):
        """default_get method is use for select default vendor #T00466"""
        vals = super(SaleOrderLine, self).default_get(fields)
        for vendors in self.product_supplier_id:
            if vendors.price_of_product == min(vendors.price_of_product):
                vals["product_supplier_id"] = vendors.partner_id.id
        return vals
