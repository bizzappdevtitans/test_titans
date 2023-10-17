# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # field for inherit in sale order line #T00466
    product_supplierinfo_id = fields.Many2one(comodel_name="product.supplierinfo", string="vendor")

    @api.model
    def default_get(self, fields):
        """default_get method is use for select default vendor #T00466"""
        vals = super(SaleOrderLine, self).default_get(fields)
        for record in self.product_supplierinfo_id:
            print("record price\n\n\n", record)
            if record.price == min(record.price):
                vals['product_supplierinfo_id'] = record.partner_id.id
                print("\n\n record.partner_id.id", record.partner_id.id)
        return vals
