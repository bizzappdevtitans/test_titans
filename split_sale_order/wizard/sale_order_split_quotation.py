from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderSplitQuotation(models.TransientModel):
    _name = "sale.order.split.quotation"
    _description = "Split Wizard"

    @api.model
    def default_get(self, field):
        """method which get reference number and set default"""
        value = super(SaleOrderSplitQuotation, self).default_get(field)
        active_id = self._context.get("active_id")
        reference = self.env["sale.order"].browse(active_id)
        value["reference"] = reference.name
        return value

    # added fields
    reference = fields.Char(string="Sale Order Reference", readonly=True)
    category = fields.Boolean(string="Base on category")

    def split_sale_order(self):
        """action for Split button"""
        if self.category == 1:
            sale = self.env["sale.order"].search([("name", "=", self.reference)])
            _no_of_category = []
            for line in sale.order_line:
                _no_of_category.append(line.product_id.categ_id)
            _no_of_category = set(_no_of_category)
            _no_of_category = list(_no_of_category)
            for _number in _no_of_category:
                sale_order = self.env["sale.order"].create(  # noqa: F841
                    {
                        "partner_id": sale.partner_id.id,
                        "source_sale_order_id": sale.name,
                    }
                )
        else:
            raise ValidationError(_("Please Select Option Based On Category !!"))
