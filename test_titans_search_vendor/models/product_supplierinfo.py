# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    # Integer field for sequence #T00466
    sequence = fields.Integer(string="Sequence")

    @api.model
    # create method for sequence #T00466
    def create(self, values):
        """this sequence is auto fill up field while create record #T00466"""
        values['sequence'] = self.env['ir.sequence'].next_by_code("product.supplierinfo")
        return super(ProductSupplierinfo, self).create(values)

    # name_get method for many2one field #T00466
    @api.depends('price', 'name')
    def name_get(self):
        # name_get method formate id [price] suppierinfo #T00466
        record_list = []
        for record in self:
            record_list.append((record.id, "[%s]  %s" % (record.price,
                                                         record.name.name)))
        return record_list
