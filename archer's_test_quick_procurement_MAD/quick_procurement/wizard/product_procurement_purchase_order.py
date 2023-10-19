from odoo import models, fields
from odoo.exceptions import ValidationError


class ProductProcurementPurchaseOrder(models.TransientModel):
    _name = "product.procurement.purchase.order"
    _description = "product procurement purchase order"

    # declaring required field #T00466
    scheduled_date = fields.Date(string="Scheduled Date")

    def _calculate_product_quantity(self, self_id):
        """declaring this method as the code block belw is used to
        calculate the final_value(total qty to be purchased, if any) #T00466"""
        sale_order_products = (
            self.env["sale.order"]
            .search([("date_order", ">", self.scheduled_date)])
            .mapped("order_line")
        )
        purchase_order_products = (
            self.env["purchase.order"]
            .search([("date_planned", ">", self.scheduled_date)])
            .mapped("order_line")
        )
        net_sale_qty = []
        net_purchase_qty = []
        required_sale_lines = []
        required_purchase_lines = []
        for sale_line in sale_order_products.ids:
            sale_order_line = self.env["sale.order.line"].browse([sale_line]).product_id
            if sale_order_line.id == self_id:
                required_sale_lines.append(sale_line)
        quantity_in_so = []
        for sale_product_quantity in required_sale_lines:
            quantity_in_so.append(
                self.env["sale.order.line"]
                .browse([sale_product_quantity])
                .product_uom_qty
            )
        net_sale_qty.append(sum(quantity_in_so))
        for purchase_line in purchase_order_products.ids:
            purchase_order_line = (
                self.env["purchase.order.line"].browse([purchase_line]).product_id
            )
            if purchase_order_line.id == self_id:
                required_purchase_lines.append(purchase_line)
        quantity_in_po = []
        for purchase_product_quantity in required_purchase_lines:
            quantity_in_po.append(
                self.env["purchase.order.line"]
                .browse([purchase_product_quantity])
                .product_qty
            )
        net_purchase_qty.append(sum(quantity_in_po))
        total_difference_so_po = sum(net_sale_qty) - sum(net_purchase_qty)
        return total_difference_so_po

    def _prepare_po_template_vals(self, variant_ids, varaint_qty):
        """this method wil be called when we are needed to create a purchase order
        for a product.template record with multiple variants #T00466"""
        values = []
        for variant in range(len(variant_ids)):
            if varaint_qty[variant] > 0:
                values.append(
                    (
                        0,
                        0,
                        {
                            "product_id": variant_ids[variant],
                            "product_qty": varaint_qty[variant],
                        },
                    )
                )
        return values

    def _create_po_template(self, vendor, variant_ids, varaint_qty):
        """when the input self_id is a template with multiple variants this method
        will be called to create the required purchase.order #T00466"""
        self.env["purchase.order"].create(
            {
                "partner_id": vendor,
                "order_line": self._prepare_po_template_vals(variant_ids, varaint_qty),
            }
        )

    def _create_po_variant(self, vendor, self_id, final_value):
        """when the input self_id is a template with only 1 variant or the self_id
        is already a variant(product.product) record this method will be called to
        create the required purchase.order #T00466"""
        self.env["purchase.order"].create(
            {
                "partner_id": vendor,
                "order_line": [
                    (
                        0,
                        0,
                        {"product_id": self_id, "product_qty": final_value},
                    )
                ],
            }
        )

    def prepare_po_quantities(self):
        """this method is used to create a purchase order if the final_value i.e.
        sale_qty - purchase_qty is not a negative value, it will be called upon
        pressing the confirm button in the wizard #T00466"""
        model = self.env.context.get("active_model")
        self_id = self.env.context.get("active_id")
        partner = self.env["res.partner"].search([]).ids
        if not self.env[model].browse([self_id]).is_product_variant:
            if self.env["product.template"].browse([self_id]).product_variant_count > 1:
                variant_ids = (
                    self.env["product.template"].browse([self_id]).product_variant_ids
                ).ids
                varaint_qty = []
                for product in variant_ids:
                    varaint_qty.append(self._calculate_product_quantity(product))
                vendor = (
                    self.env["product.product"]
                    .browse([variant_ids[0]])
                    .seller_ids.mapped("name")
                )

                if not vendor:
                    return self._create_po_template(
                        partner.ids[0], variant_ids, varaint_qty
                    )
                return self._create_po_template(vendor.ids[0], variant_ids, varaint_qty)
            # if there are no vairants the product_variant_id is used as self_id #T00466
            else:
                self_id = (
                    self.env["product.template"].browse([self_id]).product_variant_id
                ).id
            final_value = self._calculate_product_quantity(self_id)
        elif model == "product.product":
            final_value = self._calculate_product_quantity(self_id)

        if final_value > 0:
            if not vendor.ids:
                return self._create_po_variant(partner.ids[0], self_id, final_value)
            return self._create_po_variant(vendor.ids[0], self_id, final_value)
        # if final_vale < = 0 show validation error #T00466
        else:
            raise ValidationError(
                "Cannot create purchase order, already have the required amount"
            )
