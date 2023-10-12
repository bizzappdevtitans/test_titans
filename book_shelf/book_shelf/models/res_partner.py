from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    book_shelf_count = fields.Integer(compute="_compute_book")
    book_product_ids = fields.Char()

    def _compute_book(self):
        """method to count book shelf issued to partner used in smart button T-00419"""
        for record in self:
            record.book_shelf_count = self.env["book.shelf"].search_count(
                [("partner_id.id", "=", record.id)]
            )

    def action_open_book_shelf(self):
        self.ensure_one()
        if self.book_shelf_count == 1:
            return {
                "type": "ir.actions.act_window",
                "name": "Book",
                "res_model": "book.shelf",
                "view_mode": "form",
                "domain": [("partner_id.id", "=", self.id)],
                "target": "current",
            }
        return {
            "type": "ir.actions.act_window",
            "name": "Book",
            "res_model": "book.shelf",
            "view_mode": "tree,form",
            "domain": [("partner_id.id", "=", self.id)],
            "target": "current",
        }
