import datetime
from pprint import pprint

from odoo import models, fields, api


class InfragisProject(models.Model):
    _name = 'infragis.project'
    _description = 'IGIS Projekt'
    _inherit = ['mail.thread']
    _order = 'sale_order_accepted_date desc, id desc'
    _mail_post_access = 'read'

    name = fields.Char('Bezeichnung', compute='_compute_name', store=True)

    partner_id = fields.Many2one('res.partner', string="Kunde", required=True)

    introduction_date = fields.Date(string='Einschulung')
    initial_invoice_id = fields.Many2one('account.move', string="Rechnung Kauf")

    recurring_invoice_start_date = fields.Date(string="Wartungsgebühr ab", tracking=True)

    sale_order_accepted_date = fields.Date(string="Angebot akzeptiert", tracking=True)
    sale_order_sent_date = fields.Date(string="Angebot verschickt", tracking=True)

    commission_partner_id = fields.Many2one('res.partner', string="Provisions-Empfänger")

    sale_order_ids = fields.Many2many('sale.order', string="Angebot(e)", tracking=True)
    sale_order_line_ids = fields.Many2many('sale.order.line', string="Gebühren", readonly=True, store=False,
                                           compute='_search_sale_order_lines')

    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id, store=True, readonly=True)
    price_sum_total = fields.Monetary(string="Aktuelle Monatsrate", readonly=True, store=True,
                                      compute='_compute_price_sum',
                                      currency_field='currency_id', tracking=True)

    year = fields.Integer(string="Jahr", help="Dummy field for reacting to year changes", readonly=True,
                          default=datetime.datetime.now().year)

    invoices = fields.Many2many('account.move', string="Rechnungen", readonly=True, compute='_compute_invoices')

    # helper fields
    project_user_id = fields.Many2one('res.users', copy=False, tracking=True,
                                      string='Salesperson',
                                      default=lambda self: self.env.user)
    user_id = fields.Many2one(string='User', related='project_user_id',
                              help='Technical field used to fit the generic behavior in mail templates.')

    def _get_default_currency(self):
        for index in self:
            index.currency_id = self._context.get('default_currency_id')

    @api.depends('partner_id')
    def _compute_name(self):
        for project in self:
            project.name = project.partner_id.name

    @api.depends('partner_id')
    def _compute_invoices(self):
        for project in self:
            project.invoices = self.env['account.move'].search(
                [('type', '=', 'out_invoice'), '|', ('end_customer_id', '=', project.partner_id.id),
                 ('partner_id', '=', project.partner_id.id)])

    @api.depends('sale_order_line_ids', 'year')
    def _compute_price_sum(self):
        # get index for current year
        # get current year
        cur_year = datetime.datetime.now().year
        cur_index = self.env['assessment.index'].search([('name', '=', cur_year)], limit=1)
        for project in self:
            # get our current index
            project.price_sum_total = 0
            for line in project.sale_order_line_ids:
                sale_order = line.order_id
                old_index_value = sale_order.assessment_index_id.value
                project.price_sum_total += line.price_subtotal / old_index_value * cur_index.value

    @api.depends('sale_order_ids')
    def _search_sale_order_lines(self):
        for project in self:
            project.sale_order_line_ids = self.env['sale.order.line']
            for sale_order in project.sale_order_ids:
                project.sale_order_line_ids += sale_order.order_line.filtered(
                    lambda sol: sol.display_type not in ['line_section', 'line_note'])
