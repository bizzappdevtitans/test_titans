{
    "name": "Split Sale Order ",
    "version": "15.0.0.0.1",
    "author": "Bizzappdev",
    "website": "https://www.bizzappdev.com",
    "category": "Order Split",
    "depends": ["base", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/sale_order_split_quotation_view.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
    "application": True,
    "license": "AGPL-3",
}
