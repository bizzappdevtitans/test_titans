from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = 'inherited product template'

    def quick_procurement(self):
        """this is the method which will call the wizard in both product.product as
        well as product.template #T00466"""
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.procurement.purchase.order",
            "view_mode": "form",
            "target": "new",
        }
