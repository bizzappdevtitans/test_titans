from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductProcurementPurchaseOrder(models.TransientModel):
    _name = "product.procurement.purchase.order.wizard"
    _description = "Product Procurement Purchase Order"

    scheduled_date = fields.Date(required=True)
    product_variant = fields.Many2one(
        comodel_name="product.template",
        default=lambda self: self._default_product_variant_name(),
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
            # fetches sale orders #T00466
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
            # fetches purchase order  #T00466
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
            # loops throughugh product variants  #T00466
            for variants in self.product_variant.product_variant_ids:
                sale_orders = self.env["sale.order"].search(
                    [
                        (
                            "order_line.product_id",
                            "in",
                            variants.ids,
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
                            variants.ids,
                        ),
                        ("date_planned", ">", self.scheduled_date),
                        ("state", "=", "purchase"),
                    ]
                )
                total_variants_qty = {}
                total_sale_qty = sum(sale_orders.order_line.mapped("product_uom_qty"))
                total_purchase_qty = sum(
                    purchase_orders.order_line.mapped("product_qty")
                )
                # assigns the varinat id with its qty  #T00466
                total_variants_qty[variants.id] = total_sale_qty - total_purchase_qty
                # checks for any variant that has positive qty  #T00466
                if not any(total_qty > 0 for total_qty in total_variants_qty.values()):
                    raise ValidationError(_("No positive qty product variant"))
                order_lines = []
                for variants, total_qty in total_variants_qty.items():
                    order_lines.append(
                        (
                            0,
                            0,
                            {
                                "product_id": variants,
                                "product_qty": total_qty,
                            },
                        )
                    )

            self.env["purchase.order"].create(
                {
                    "partner_id": self.partner_id.id,
                    "order_line": order_lines,
                }
            )

    def action_cancel(self):
        """Action for cancel button #T00466"""

    @api.model
    def _default_product_variant_name(self):
        """function to get current id of product in wizard #T00466"""
        context = dict(self._context) or {}
        product_temp = self.env["product.template"].browse(
            context.get("active_id", False)
        )
        return product_temp and product_temp.id
