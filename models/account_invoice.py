from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'
    end_customer_id = fields.Many2one('res.partner', string="Endkunde", readonly=True,
                                      states={'draft': [('readonly', False)]})
