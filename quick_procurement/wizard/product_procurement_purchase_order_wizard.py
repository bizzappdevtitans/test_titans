from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductProcurementPurchaseOrder(models.TransientModel):
    _name = "product.procurement.purchase.order.wizard"
    _description = "Product Procurement Purchase Order"

    scheduled_date = fields.Date(required=True)
    product_template = fields.Many2one(
        comodel_name="product.template",
        default=lambda self: self._default_product_template_name(),
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Vendor", required=True
    )

    def create_purchase_order_from_product(self):
        """function that will create purchase order from product with values from
        product #T00466"""
        model = self.env.context.get("active_model")
        product_id = self.env.context.get("active_id")
        if model == "product.product":
            sale_orders = self.env["sale.order"].search(
                [
                    (
                        "order_line.product_id",
                        "=",
                        product_id,
                    ),
                    ("date_order", ">", self.scheduled_date),
                    ("state", "=", "sale"),
                ]
            )
            purchase_orders = self.env["purchase.order"].search(
                [
                    (
                        "order_line.product_id",
                        "=",
                        product_id,
                    ),
                    ("date_planned", ">", self.scheduled_date),
                    ("state", "=", "purchase"),
                ]
            )

            total_sale_qty = sum(sale_orders.order_line.mapped("product_uom_qty"))
            total_purchase_qty = sum(purchase_orders.order_line.mapped("product_qty"))
            total_qty = total_sale_qty - total_purchase_qty

            if total_qty < 0:
                raise ValidationError(_("Cant Purchase more"))
            vals = {
                "partner_id": self.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_id,
                            "product_qty": total_qty,
                        },
                    )
                ],
            }
            self.env["purchase.order"].create(vals)
        else:
            sale_orders = self.env["sale.order"].search(
                [
                    (
                        "order_line.product_id",
                        "in",
                        self.product_template.product_variant_ids.ids,
                    ),
                    ("date_order", ">", self.scheduled_date),
                    ("state", "=", "sale"),
                ]
            )
            purchase_orders = self.env["purchase.order"].search(
                [
                    (
                        "order_line.product_id",
                        "in",
                        self.product_template.product_variant_ids.ids,
                    ),
                    ("date_planned", ">", self.scheduled_date),
                    ("state", "=", "purchase"),
                ]
            )
            total_sale_qty = sum(sale_orders.order_line.mapped("product_uom_qty"))
            total_purchase_qty = sum(purchase_orders.order_line.mapped("product_qty"))
            total_qty = total_sale_qty - total_purchase_qty
            if total_qty < 0:
                raise ValidationError(_("Cant Purchase more"))
            order_lines = []
            for orders in sale_orders.order_line.product_id.ids:
                order_lines.append(
                    (
                        0,
                        0,
                        {
                            "product_id": orders,
                            "product_qty": total_qty,
                        },
                    )
                )

            self.env["purchase.order"].create(
                {"partner_id": self.partner_id.id, "order_line": order_lines}
            )

    def action_cancel(self):
        """Action for cancel button #T00466"""
        return

    @api.model
    def _default_product_template_name(self):
        """function to get current id of product in wizard #T00466"""
        context = dict(self._context) or {}
        product_temp = self.env["product.template"].browse(
            context.get("active_id", False)
        )
        return product_temp and product_temp.id
