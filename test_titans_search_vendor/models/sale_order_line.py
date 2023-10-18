# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # field for inherit in sale order line #T00466
    product_supplierinfo_id = fields.Many2one(comodel_name="product.supplierinfo", string="vendor")

    # inherit method for update vendor #T00466
    @api.onchange('product_id')
    def _update_description(self):
        """this method call when we select the product in sale order line #T00466"""
        super(SaleOrderLine, self)._update_description()
        product_supplierinfo = self.env['product.supplierinfo'].search([])

        # below mapped function get record price, delay time and vendor_number #T00466
        vendor_price = product_supplierinfo.mapped(lambda lm: lm.price)
        vendor_lead_time = product_supplierinfo.mapped(lambda lm: lm.delay)
        vendor_sequence = product_supplierinfo.mapped(lambda lm: lm.vendor_number)

        # below sorted method is use for sort price, delay time and sequence #T00466
        vendor_price_sorted = sorted(vendor_price)
        vendor_lead_time_sorted = sorted(vendor_lead_time)
        vendor_sequence_sorted = sorted(vendor_sequence)

        record_list = []
        vendor_lead_time_list = []
        vendor_sequence_list = []

        # this for method append only that record have minimum price #T00466
        for record in product_supplierinfo:
            if record.price == vendor_price_sorted[0]:
                record_list.append(record.id)

        # this for method append only that record have minimum delay time #T00466
        for record in product_supplierinfo:
            if record.delay == vendor_lead_time_sorted[0]:
                vendor_lead_time_list.append(record.id)

        # this for method append only that record have minimum sequence #T00466
        for record in product_supplierinfo:
            if record.vendor_number == vendor_sequence_sorted[0]:
                vendor_sequence_list.append(record.id)

        # loop for is update the record according to their minimum values #T00466
        for record in product_supplierinfo:
            if len(record_list) == 1:
                """this statement check record_list have only one record #T00466"""
                self.update({'product_supplierinfo_id': record_list[0]})
            elif len(vendor_lead_time_list) == 1:
                """this statement check vendor_lead_time_list have only one record #T00466"""
                self.update({'product_supplierinfo_id': vendor_lead_time_list[0]})
            else:
                """this statement check vendor_sequence_list have only one record #T00466"""
                self.update({'product_supplierinfo_id': vendor_sequence_list[0]})
