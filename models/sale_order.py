from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    assessment_index_id = fields.Many2one('assessment.index', string="Berechnungsgrundlage")
