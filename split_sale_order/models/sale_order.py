from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # added field
    source_sale_order_id = fields.Char(
        string="Source Sale Order Reference", readonly=True
    )
