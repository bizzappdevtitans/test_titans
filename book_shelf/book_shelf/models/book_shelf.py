from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class BookShelf(models.Model):
    _name = "book.shelf"
    _description = "Book Shelf"
    _rec_name = "sequence"
    _order = "sequence DESC"

    # T-00419
    sequence = fields.Char(
        string="sequence",
        required=True,
        readonly=True,
        copy=False,
        index=True,
        default=lambda self: ("New"),
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Member")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("process", "Process"),
            ("confirm", "Confirm"),
            ("cancel", "Cancel"),
            ("done", "Done"),
        ],
        default="draft",
    )
    book_shelf_line = fields.One2many(
        comodel_name="book.shelf.line", inverse_name="book_shelf_id"
    )
    sale_order_ref = fields.Char(string="Sale Order Reference")
    total = fields.Float(string="Total")
    note = fields.Char()

    def copy(self):
        """inherited copy method T-00426"""
        raise ValidationError("cannot copy book order")

    @api.model
    def create(self, vals):
        """inheriting create method to set sequence T-00419"""
        if vals.get("sequence", _("New")) == _("New"):
            vals["sequence"] = self.env["ir.sequence"].next_by_code("book.shelf") or _(
                "New"
            )
        result = super().create(vals)
        return result

    def create_sale_order_line_value(self, line):
        """These Function is to create sale order line Value T-00419"""
        self.ensure_one()
        return {
            "product_id": line.product_id.id,
            "product_uom_qty": line.qty,
            "price_unit": line.price,
            "min_day": line.min_day,
            "max_day": line.max_day,
            "late_fee": line.late_fee,
        }

    def create_sale_order_value(self):
        """These Function is to create sale order T-00419"""
        return {
            "partner_id": self.partner_id.id,
            "order_line": [],
            "client_order_ref": self.sequence,
        }

    def create_sale_order(self):
        """These function is use to create sale order T-00419"""
        values = self.create_sale_order_value()
        for line in self.book_shelf_line:
            values["order_line"].append((0, 0, self.create_sale_order_line_value(line)))
        self.sale_order_ref = (self.env["sale.order"].sudo().create(values)).name

    def action_confirm(self):
        """this function create sale order and also set book shelf in process state T-00419"""
        self.create_sale_order()
        self.write({"state": "process"})

    def action_open_sale_order(self):
        """these open particular sale order T-00426"""
        return {
            "type": "ir.actions.act_window",
            "name": "Sale order",
            "res_model": "sale.order",
            "view_mode": "form",
            "res_id": self.env["sale.order"]
            .search([("client_order_ref", "=", self.sequence)], limit=1)
            .id,
            "target": "current",
        }

    def action_cancel(self):
        """these will cancel sale order and book shelf T-00426"""
        self.env["sale.order"].search(
            [("name", "=", self.sale_order_ref)]
        ).action_cancel()
        self.state = "cancel"

    @api.depends("book_shelf_line.price", "book_shelf_line.qty")
    def return_book(self):
        """function to return book T-00419"""
        self.ensure_one()
        late_fee = 0.00
        amount = 0.00
        for line in self.book_shelf_line:
            return_day = date.today()
            min_return_day = line.issue_date + timedelta(days=line.min_day)
            max_return_day = line.issue_date + timedelta(days=line.max_day)
            if return_day < min_return_day:
                raise UserError(_("you cannot return the book."))
            if return_day > max_return_day:
                day = (return_day - line.issue_date).days
                late_fee += (line.product_id.late_fee) * day
            amount += line.qty * line.price
        if late_fee:
            self.note = "Late Fee is added for returning book after max day"
        self.total = amount + late_fee
        self.write({"state": "done"})
