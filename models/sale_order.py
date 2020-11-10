import datetime

from odoo import models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _order = 'igis_date desc'

    assessment_index_id = fields.Many2one('assessment.index', string="Berechnungsgrundlage")
    igis_project_id = fields.Many2one('infragis.project', string="IGIS Projekt", readonly=True, tracking=True)
    igis_date = fields.Date(string='Angebotsdatum', required=False, default=datetime.datetime.now())

    def generate_project(self):
        self.ensure_one()

        # open the project in edit mode
        return {
            'name': 'Projekt anlegen',
            'view_mode': 'tree,form',
            'views': [(False, 'form')],
            'res_model': 'infragis.project',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_sale_order_ids': [self.id]
            }
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # inherit base index from sale_order for calculating sums
    assessment_index_id = fields.Many2one('assessment.index', related='order_id.assessment_index_id',
                                          string="Berechnungsgrundlage")

    def _prepare_invoice_line_wqty(self, year, qty=3):
        self.ensure_one()

        # scale price by index
        price_unit = self.price_unit

        cur_index = self.env['assessment.index'].search([('name', '=', year)], limit=1)
        if len(cur_index) == 0:
            raise UserError(('Keine Berechnungsgrundlage für Jahr {}'.format(year)))

        old_index_value = self.assessment_index_id.value
        price_unit = price_unit / old_index_value * cur_index.value

        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': qty,
            'discount': self.discount,
            'price_unit': price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        if self.display_type:
            res['account_id'] = False
        return res

    def _prepare_invoice_line_section(self, name):
        self.ensure_one()

        res = {
            'display_type': 'line_section',
            'sequence': self.sequence,
            'name': name,
            'product_id': None,
            'product_uom_id': None,
            'quantity': 0,
            'discount': 0,
            'price_unit': 0,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'account_id': False
        }

        return res
