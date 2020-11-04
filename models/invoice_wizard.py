import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api


class InfragisWizard(models.TransientModel):
    _name = 'infragis.invoice.wizard'
    _description = 'Wizard for generating invoices from projects'

    project_ids = fields.Many2many('infragis.project', string="Projekte")

    quarter = fields.Selection(selection=lambda self: self._compute_quarter_list(), required=True,
                               string="Generieren bis inkl. Quartal")

    @api.model
    def _compute_quarter_list(self):
        # get current date and get the quarter before and the next one
        cur_date = datetime.datetime.now().date()
        cur_month = cur_date.month
        cur_quarter = (cur_month // 3) + 1

        last_quarter_date = cur_date + relativedelta(months=-3)
        last_quarter = (last_quarter_date.month // 3) + 1

        next_quarter_date = cur_date + relativedelta(months=+3)
        next_quarter = (next_quarter_date.month // 3) + 1

        select = [
            ('{}|{}'.format(last_quarter, last_quarter_date.year),
             'Q{} {}'.format(last_quarter, last_quarter_date.year)),
            ('{}|{}'.format(cur_quarter, cur_date.year), 'Q{} {}'.format(cur_quarter, cur_date.year)),
            ('{}|{}'.format(next_quarter, next_quarter_date.year),
             'Q{} {}'.format(next_quarter, next_quarter_date.year))
        ]

        return select

    @api.model
    def default_get(self, fields):
        res = super(InfragisWizard, self).default_get(fields)
        project_ids = self.env.context.get('active_ids')
        res.update({
            'project_ids': project_ids
        })
        return res

    def action_generate_invoices(self):
        # get option from selection field
        quarter_sel = self.quarter
        print(quarter_sel)
        [quarter, year] = [int(s) for s in quarter_sel.split('|')]

        project_ids = []
        # start 3 years ago
        year -= 3
        for x in range(12):
            quarter += 1
            if quarter >= 5:
                year += 1
                quarter = 1
            print("Generating for Q{}/{}".format(quarter, year))
            project_ids.append(self.project_ids.generate_invoice(quarter, year))
        return project_ids
