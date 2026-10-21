from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    kitchen_ref = fields.Char(
        string="Kitchen configurator reference",
        index='btree_not_null',
        copy=False,
        help="Reference of the item in the 3D kitchen configurator (catalogue id, accessory-…, worktop…).",
    )
