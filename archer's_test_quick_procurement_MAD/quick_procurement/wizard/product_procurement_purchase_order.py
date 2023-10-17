from odoo import models, fields
from odoo.exceptions import ValidationError


class ProductProcurementPurchaseOrder(models.TransientModel):
    _name = "product.procurement.purchase.order"
    _description = "product procurement purchase order"

    scheduled_date = fields.Date(string="Scheduled Date")

    def fetch_sale_order(self):
        """this method is used to create a purchase order if the final_value i.e.
        sale_qty - purchase_qty is not a negative value #T00466"""
        model = self.env.context.get("active_model")
        self_id = self.env.context.get("active_id")
        sale_order = self.env["sale.order"].search(
            [("date_order", ">", self.scheduled_date)]
        )
        purchase_order = self.env["purchase.order"].search(
            [("date_planned", ">", self.scheduled_date)]
        )
        sale_order_products = sale_order.mapped("order_line")
        purchase_order_products = purchase_order.mapped("order_line")
        required_sale_lines = []
        quantity_in_so = []
        required_purchase_lines = []
        quantity_in_po = []
        if model == "product.template":
            # checking if the there are multiple variants
            if self.env["product.template"].browse([self_id]).product_variant_count > 1:
                variants = (
                    self.env["product.template"].browse([self_id]).product_variant_ids
                )
                net_sale_qty = []
                net_purchase_qty = []
                # there are multiple variants we will find the SO_qty & PO_qty for all
                # variants
                for product in variants.ids:
                    self_id = product
                    # calculating the number of sale order quantity
                    for sale_line in sale_order_products.ids:
                        sale_order_line = (
                            self.env["sale.order.line"].browse([sale_line]).product_id
                        )
                        if sale_order_line.id == self_id:
                            required_sale_lines.append(sale_line)
                    for sale_product_quantity in required_sale_lines:
                        quantity_in_so.append(
                            self.env["sale.order.line"]
                            .browse([sale_product_quantity])
                            .product_uom_qty
                        )
                    # total quantity fetched from sale order
                    net_sale_qty.append(sum(quantity_in_so))

                    # calculating the number of purchase order quantity

                    for purchase_line in purchase_order_products.ids:
                        purchase_order_line = (
                            self.env["purchase.order.line"]
                            .browse([purchase_line])
                            .product_id
                        )
                        if purchase_order_line.id == self_id:
                            required_purchase_lines.append(purchase_line)
                    for purchase_product_quantity in required_purchase_lines:
                        quantity_in_po.append(
                            self.env["purchase.order.line"]
                            .browse([purchase_product_quantity])
                            .product_qty
                        )
                    net_purchase_qty.append(sum(quantity_in_po))
                # TODO make a create method
                return
            # if there are no vairants we apply the same logic as the code in elif but
            # by assigning a diffrent self_id
            else:
                # as there are no variants so we find the product's variant id
                # and update self_id
                self_id = (
                    self.env["product.template"].browse([self_id]).product_variant_id
                ).id
                for sale_line in sale_order_products.ids:
                    # checking for the products used in the sale order lines
                    sale_order_line = (
                        self.env["sale.order.line"].browse([sale_line]).product_id
                    )
                    if sale_order_line.id == self_id:
                        required_sale_lines.append(sale_line)
                for sale_product_quantity in required_sale_lines:
                    quantity_in_so.append(
                        self.env["sale.order.line"]
                        .browse([sale_product_quantity])
                        .product_uom_qty
                    )
                # total quantity fetched from sale order
                net_sale_qty = sum(quantity_in_so)

                # calculating the number of purchase order quantity

                purchase_order_products = purchase_order.mapped("order_line")
                for purchase_line in purchase_order_products.ids:
                    purchase_order_line = (
                        self.env["purchase.order.line"]
                        .browse([purchase_line])
                        .product_id
                    )
                    if purchase_order_line.id == self_id:
                        required_purchase_lines.append(purchase_line)
                for purchase_product_quantity in required_purchase_lines:
                    quantity_in_po.append(
                        self.env["purchase.order.line"]
                        .browse([purchase_product_quantity])
                        .product_qty
                    )
                net_purchase_qty = sum(quantity_in_po)
            final_value = net_sale_qty - net_purchase_qty

        elif model == "product.product":
            # calculating the number of sale order quantity
            for sale_line in sale_order_products.ids:
                sale_order_line = (
                    self.env["sale.order.line"].browse([sale_line]).product_id
                )
                if sale_order_line.id == self_id:
                    required_sale_lines.append(sale_line)
            for sale_product_quantity in required_sale_lines:
                quantity_in_so.append(
                    self.env["sale.order.line"]
                    .browse([sale_product_quantity])
                    .product_uom_qty
                )
            # total quantity fetched from sale order
            net_sale_qty = sum(quantity_in_so)

            # calculating the number of purchase order quantity

            for purchase_line in purchase_order_products.ids:
                purchase_order_line = (
                    self.env["purchase.order.line"].browse([purchase_line]).product_id
                )
                if purchase_order_line.id == self_id:
                    required_purchase_lines.append(purchase_line)
            for purchase_product_quantity in required_purchase_lines:
                quantity_in_po.append(
                    self.env["purchase.order.line"]
                    .browse([purchase_product_quantity])
                    .product_qty
                )
            net_purchase_qty = sum(quantity_in_po)
            final_value = net_sale_qty - net_purchase_qty
        # creating a PO
        vendor = (
            self.env["product.product"].browse([self_id]).seller_ids.mapped("name")
        ).id
        # if no vendor is predifined we eill add the 1st partner_id we find
        if final_value > 0:
            if not vendor:
                partner = self.env["res.partner"].search([])
                return self.env["purchase.order"].create(
                    {
                        "partner_id": partner.ids[0],
                        "order_line": [
                            (
                                0,
                                0,
                                {"product_id": self_id, "product_qty": final_value},
                            )
                        ],
                    }
                )
            # else assign the vendor that was found
            else:
                return self.env["purchase.order"].create(
                    {
                        "partner_id": vendor,
                        "order_line": [
                            (0, 0, {"product_id": self_id, "product_qty": final_value})
                        ],
                    }
                )
        else:
            raise ValidationError("already have teh required amount!")
