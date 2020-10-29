from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    assessment_index_id = fields.Many2one('assessment.index', string="Berechnungsgrundlage")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # inherit base index from sale_order
    assessment_index_id = fields.Many2one('assessment.index', related='order_id.assessment_index_id', string="Berechnungsgrundlage")
