from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    # T-00419
    max_day = fields.Integer()
    min_day = fields.Integer()
    late_fee = fields.Float()
