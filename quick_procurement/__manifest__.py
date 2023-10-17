{
    "name": "quick_procurement",
    "summary": """""",
    "author": "bizzappdev",
    "website": "http://bizzappdev.com",
    "category": "Uncategorized",
    "version": "15.0.1.0.0",
    "depends": ["base", "sale", "sale_management", "purchase", "product"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/product_procurement_purchase_order_wizard_views.xml",
        "views/product_views.xml",
        "views/product_template_views.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}
