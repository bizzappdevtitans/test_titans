# -*- coding: utf-8 -*-
{
    'name': "quick_procurement",
    'author': "BizzAppDev",
    'website': "http://www.bizzappdev.com",
    'license': 'LGPL-3',
    'version': '15.0.0.0.0',
    'depends': ['product', 'purchase', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_procurement_purchase_order_view.xml',
        'views/product_template_view.xml',
    ],
    'installable': True,
    'application': True,
}
