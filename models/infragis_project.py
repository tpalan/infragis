import datetime
from pprint import pprint

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import UserError


class InfragisProject(models.Model):
    _name = 'infragis.project'
    _description = 'GIS Projekt'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _mail_post_access = 'read'

    name = fields.Char('Bezeichnung')

    partner_id = fields.Many2one('res.partner', string="Kunde", required=True)

    introduction_date = fields.Date(string='Einschulung')

    initial_invoice_id = fields.Many2one('account.move', string="Rechnung Kauf")
    initial_invoice_date = fields.Date('Datum', related='initial_invoice_id.invoice_date')
    initial_invoice_period = fields.Char('Zeitraum', related='initial_invoice_id.period')
    initial_invoice_amount = fields.Monetary('Kauf netto', related='initial_invoice_id.amount_untaxed')

    recurring_invoice_start_date = fields.Date(string="Wartungsgebühr ab", tracking=True)
    recurring_invoice_stop_date = fields.Date(string="Wartungsgebühr bis", tracking=True)

    #sale_order_accepted_date = fields.Date(string="Angebot akzeptiert", tracking=True)
    #sale_order_sent_date = fields.Date(string="Angebot verschickt", tracking=True)
    # sale_order_attachment = fields.Many2many('ir.attachment', string="Angebots-Dokument")

    commission_partner_id = fields.Many2one('res.partner', string="Provision an")

    sale_order_ids = fields.One2many('sale.order', 'igis_project_id', string="Angebot(e)", tracking=True)
    sale_order_line_ids = fields.Many2many('sale.order.line', string="Gebühren", readonly=True, store=False,
                                           compute='_compute_sale_order_lines')

    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id, store=True, readonly=True)
    price_sum_total = fields.Monetary(string="Monatsrate", readonly=True, store=True,
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

    @api.onchange('partner_id')
    def _change_partner_id(self):
        for project in self:
            if project.name is False:
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

    @api.depends('sale_order_ids', 'sale_order_ids.amount_untaxed')
    def _compute_sale_order_lines(self):
        for project in self:
            project.sale_order_line_ids = self.env['sale.order.line']
            for sale_order in project.sale_order_ids:
                project.sale_order_line_ids += sale_order.order_line.filtered(
                    lambda sol: (sol.display_type not in ['line_section',
                                                          'line_note'] and sol.product_id.product_tmpl_id.categ_id.id == 4))

    def generate_invoice(self, quarter=0, year=0):

        if quarter == 0:
            quarter = (datetime.datetime.now().date().month // 3) + 1
        if year == 0:
            year = datetime.datetime.now().date().year

        # format Leistungszeitraum, e.g. "Q1 2020"
        period = 'Q{} {}'.format(quarter, year)
        invoice_ids = []

        for project in self:
            # check if we need to bill anything
            if not (project.recurring_invoice_start_date):
                print("No start date in project {} ({})".format(project.id, project.name))
                continue
            # check if we have at least one month to invoice
            # the first day to invoice has to be earlier than the first day of the last month of the quarter
            last_month = (quarter * 3)

            last_month_date = datetime.datetime.now().date().replace(year=year, month=last_month, day=1)
            # print("first day of last month of quarter: {}".format(last_month_date))

            if project.recurring_invoice_start_date > last_month_date:
                print("Start date {} in project {} ({}) is later than first day of last month of quarter ({})".format(
                    project.recurring_invoice_start_date, project.id, project.name, last_month_date))
                continue

            # check if start date is before first day of quarter
            quantity = 0
            first_month = (quarter * 3) - 2
            recurring_invoice_start_date = project.recurring_invoice_start_date

            # fix start of month (if it is first day of the month, use last day of previous month for calculation)
            if recurring_invoice_start_date.day == 1:
                recurring_invoice_start_date += relativedelta(days=-1)

            first_day_date = datetime.datetime.now().date().replace(year=year, month=first_month, day=1)
            if recurring_invoice_start_date <= first_day_date:
                quantity = 3  # full quarter
            else:
                # calculate remaining months
                quantity = last_month - recurring_invoice_start_date.month

            print("after start-date: quantitiy is now {}".format(quantity))

            # check end date
            if project.recurring_invoice_stop_date:
                second_month = (quarter * 3) - 1
                second_month_date = datetime.datetime.now().date().replace(year=year, month=second_month, day=1)
                if project.recurring_invoice_stop_date < second_month_date:
                    print(
                        "Stop date {} in project {} ({}) is earlier than first day of the second month of the quarter ({})".format(
                            project.recurring_invoice_stop_date, project.id, project.name, second_month_date))
                    continue
                # calculate number of months to bill
                last_day = datetime.datetime.now().date().replace(year=year, month=last_month, day=1) + relativedelta(
                    months=1) + relativedelta(days=-1)
                if project.recurring_invoice_stop_date <= last_day:
                    # reduce quantity
                    quantity -= (last_month - project.recurring_invoice_stop_date.month) + 1
            print("after stop-date: quantitiy is now {}".format(quantity))

            if quantity <= 0:
                print("Nothing to bill in project {} ({})", project.id, project.name)
                continue

            invoice_origin = 'IGIS{}'.format(project.id)

            invoice_vals = None
            create = True

            for sale_order in project.sale_order_ids:
                #if not (sale_order.igis_date):
                #    raise UserError(('Keine Angebotsdatum für Projekt {}'.format(project.name)))
                if invoice_vals == None:

                    # look if we already have an invoice with this period & partner_id & project
                    if len(self.env['account.move'].search(
                            [('period', '=', period), ('partner_id', '=', project.partner_id.id),
                             ('igis_project_id', '=', project.id)])) > 0:
                        print("Invoice for period {} already exists in project {} ({})".format(period, project.id,
                                                                                               project.name))
                        create = False
                        break
                    invoice_vals = sale_order._prepare_invoice()

                # add all lines from sale_order as invoice_lines
                # add a section with the sale_order_sent_date before
                first = True
                for sale_order_line in sale_order.order_line.filtered(
                        lambda sol: (sol.display_type not in ['line_section',
                                                              'line_note'] and sol.product_id.product_tmpl_id.categ_id.id == 4)):
                    # create section
                    if first == True:
                        if sale_order.igis_date:
                            formatted_date = sale_order.igis_date.strftime('%d.%m.%Y')
                            section_name = 'InfraGIS Wartungsgebühr lt. Angebot vom {}'.format(formatted_date)
                        else:
                            section_name = 'InfraGIS Wartungsgebühr'
                        invoice_vals['invoice_line_ids'].append(
                            (0, None, sale_order_line._prepare_invoice_line_section(section_name)))
                        first = False
                    invoice_line_vals = sale_order_line._prepare_invoice_line_wqty(year, quantity)
                    invoice_vals['invoice_line_ids'].append((0, None, invoice_line_vals))

            if create:
                invoice_vals['period'] = period
                invoice_vals['invoice_origin'] = invoice_origin
                invoice_vals['end_customer_id'] = project.partner_id
                invoice_vals['igis_project_id'] = project

                # create invoice draft
                invoice = self.env['account.move'].create(invoice_vals)
                invoice_ids.append(invoice.id)

        return invoice_ids
