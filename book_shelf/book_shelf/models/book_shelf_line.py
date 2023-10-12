from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BookShelf(models.Model):
    _name = "book.shelf.line"
    _description = "Book Shelf Line"
    # T-00419
    book_shelf_id = fields.Many2one(
        comodel_name="book.shelf",
    )
    partner_id = fields.Many2one(related="book_shelf_id.partner_id", store=True)
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain="[('categ_id.name','=','Book')]",
        ondelete="restrict",
        check_company=True,
    )
    product_template_id = fields.Many2one(
        "product.template",
        string="Product Template",
        related="product_id.product_tmpl_id",
        domain="[('categ_id.is_book','=',True)]",
    )
    price = fields.Float(
        string="Price", related="product_id.list_price", store=True, readonly=False
    )
    qty = fields.Float(string="Quntatity", default=1)
    max_day = fields.Integer(
        string="Max day", help="maxmium number of day to return a book"
    )
    min_day = fields.Integer(
        string="Min day", help="minimum number of day to return a book"
    )
    issue_date = fields.Date(readonly=True)
    late_fee = fields.Float(related="product_id.late_fee")

    def name_get(self):
        """name get method for line T-00426"""
        name = []
        for line in self:
            name.append(
                (
                    line.product_id.id,
                    "[%s]-%s" % (line.product_id.default_code, line.product_id.name),
                )
            )
        return name

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        """name search method for order line T-00426"""
        args = args or []
        domain = []
        if name:
            domain = [
                "|",
                ("product_id.name", operator, name),
                ("book_shelf_id.name", operator, name),
            ]

        return self.search(domain + args, limit=limit).name_get()

    @api.constrains("min_day", "max_day")
    def _check_day(self):
        """validating min and max day T-00426"""
        for record in self:
            if record.min_day > record.max_day:
                raise ValidationError("please check min_day and max_day")

    @api.constrains("product_id")
    def _check_book_line(self):
        """Function for set validation error if the book is already issued to partner
        in the previous book order T-00419"""
        for record in self:
            recordset = self.env["book.shelf"].search(
                [
                    ("partner_id", "=", record.book_shelf_id.partner_id.id),
                    ("id", "!=", record.book_shelf_id.id),
                ]
            )
            if recordset:
                booklist = []
                for bookshelf in recordset:
                    value = []
                    for line in bookshelf.book_shelf_line:
                        value.append(line.product_id.id)
                    booklist.extend(value)
                if booklist:
                    if record.product_id.id in booklist:
                        raise ValidationError(
                            "These Product is already assigned to partner"
                        )
