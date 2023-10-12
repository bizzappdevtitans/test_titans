from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"
    # T-00419
    author = fields.Char(string="Author?")
    book_ok = fields.Boolean(string="Is Book?")
