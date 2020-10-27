from odoo import models, fields, api

class InfragisProject(models.Model):
    _name = 'infragis.project'
    _description = 'IGIS Projekt'
    partner_id = fields.Many2one('res.partner', string="Kunde", required=True)
    alt_customer_id = fields.Many2one('res.partner', string="Alt. Re-Empfänger")
    customer_id = fields.Many2one('res.partner', string="Re-Empfänger", readonly=True, store=True, compute='_compute_customer_id')
    introduction_date = fields.Date(string='Einschulung')
    initial_invoice_id = fields.Many2one('account.move', string="Initiale Rechnung")

    @api.depends('alt_customer_id')
    def _compute_customer_id(self):
        for project in self:
            if project.alt_customer_id:
                project.customer_id = project.alt_customer_id
            else:
                project.customer_id = project.partner_id

