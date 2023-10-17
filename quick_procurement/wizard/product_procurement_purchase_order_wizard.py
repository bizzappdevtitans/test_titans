from odoo import models, fields, api

from odoo.exceptions import ValidationError


class ProductProcurementPurchaseOrder(models.TransientModel):
    _name = "product.procurement.purchase.order.wizard"
    _description = "Product Procurement Purchase Order"

    scheduled_date = fields.Date(string="Scheduled Date")
    product = fields.Many2one(
        comodel_name="product.product",
        default=lambda self: self._default_product_name(),
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Vendor")

    def create_purchase_order_from_product(self):
        """function that will create purchase order from product with values from
        product #T00466"""
        sale_orders = self.env["sale.order"].search(
            [
                ("order_line.product_id", "=", self.product.id),
                ("date_order", ">", self.scheduled_date),
                ("state", "=", "sale"),
            ]
        )
        purchase_orders = self.env["purchase.order"].search(
            [
                ("order_line.product_id", "=", self.product.id),
                ("date_planned", ">", self.scheduled_date),
                ("state", "=", "purchase"),
            ]
        )
        for orders in sale_orders and purchase_orders:
            result = orders.order_line.product_uom_qty - orders.order_line.product_qty
            if result < 0:
                raise ValidationError("Cant Purchase more")
            vals = {
                "partner_id": self.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {"product_id": self.product.id, "product_qty": result},
                    )
                ],
            }

        self.env["purchase.order"].create(vals)

    def action_cancel(self):
        """Action for cancel button #T00466"""
        pass

    @api.model
    def _default_product_name(self):
        """function to get default name of product in wizard #T00466"""
        context = dict(self._context) or {}
        product = self.env["product.product"].browse(context.get("active_id", False))
        return product and product.id
