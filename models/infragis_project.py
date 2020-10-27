from odoo import models, fields, api

class InfragisProject(models.Model):
    _name = 'infragis.project'
    _description = 'IGIS Projekt'
    name = fields.Char(required=True)
    end_customer_id = fields.Many2one('res.partner', string="Endkunde", required=True)
    alt_customer_id = fields.Many2one('res.partner', string="Alt. Re-Empfänger")
    customer_id = fields.Many2one('res.partner', string="Re-Empfänger", readonly=True, store=True, compute='_compute_customer_id')

    @api.depends('alt_customer_id')
    def _compute_customer_id(self):
        for project in self:
            if project.alt_customer_id:
                project.customer_id = project.alt_customer_id
            else:
                project.customer_id = project.end_customer_id

