from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    late_fee = fields.Float()

    def name_get(self):
        name = []
        for product in self:
            if not product.categ_id.name == "Book":
                return super().name_get()
            name.append(
                (
                    product.id,
                    "%s by %s" % (product.name, product.author),
                )
            )
        return name

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                "|",
                ("name", operator, name),
                ("author", operator, name),
            ]
        return self.search(domain + args, limit=limit).name_get()
