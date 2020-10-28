from odoo import models, fields, api


class InfragisProject(models.Model):
    _name = 'infragis.project'
    _description = 'IGIS Projekt'

    name = fields.Char(
        'Bezeichnung', compute='_compute_name', store=True)

    partner_id = fields.Many2one('res.partner', string="Kunde", required=True)
    # alt_customer_id = fields.Many2one('res.partner', string="Alt. Re-Empfänger")
    # customer_id = fields.Many2one('res.partner', string="Re-Empfänger", readonly=True, store=True, compute='_compute_customer_id')
    introduction_date = fields.Date(string='Einschulung')
    initial_invoice_id = fields.Many2one('account.move', string="Initiale Rechnung")

    recurring_invoice_start_date = fields.Date(string="Wartungsgebühr ab")

    commission_partner_id = fields.Many2one('res.partner', string="Provisions-Kunde")

    sale_order_id = fields.Many2one('sale.order', string="Angebot")
    sale_order_line_ids = fields.Many2many('sale.order.line', string="Rechnungs-Positionen", readonly=True, store=True,
                                           compute='_compute_sale_order_lines')
    assessment_index_id = fields.Many2one('assessment.index', string="Berechnungsgrundlage", readonly=True,
                                          compute='_compute_assessment_index')

    invoices = fields.Many2many('account.move', string="Rechnungen", readonly=True, compute='_compute_invoices')

    @api.depends('partner_id')
    def _compute_name(self):
        for project in self:
            project.name = project.partner_id.name

    @api.depends('partner_id')
    def _compute_invoices(self):
        for project in self:
            project.invoices = self.env['account.move'].search(
                [('type', '=', 'out_invoice'),'|', ('end_customer_id', '=', project.partner_id.id), ('partner_id', '=', project.partner_id.id)])


    @api.depends('sale_order_id')
    def _compute_sale_order_lines(self):
        for project in self:
            if project.sale_order_id:
                project.sale_order_line_ids = project.sale_order_id.order_line.filtered(
                    lambda so: so.display_type not in ['line_section', 'line_note'])

    @api.depends('sale_order_id')
    def _compute_assessment_index(self):
        for project in self:
            if project.sale_order_id:
                project.assessment_index_id = project.sale_order_id.assessment_index_id
            else:
                project.assessment_index_id = None
