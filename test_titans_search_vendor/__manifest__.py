# -*- coding: utf-8 -*-
{
    'name': "search vendor",

    'summary': """search vendor""",

    'description': """
        search vendor
    """,

    'author': "BizzAppDev",
    'website': "http://www.bizzappdev.com",
    'version': '15.0.0.1',
    'depends': ['base', 'purchase', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/product_supplierinfo_data.xml',
        'views/product_supplierinfo_views.xml',
        'views/sale_order_view.xml',
    ],
}
