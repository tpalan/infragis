from odoo import models, fields


class AssessmentIndex(models.Model):
    _name = 'assessment.index'
    _description = 'Index'

    year = fields.Integer('Jahr', required=True) # TODO: format without thousand seperator
    currency_id = fields.Many2one('res.currency', string="Currency", compute='_get_default_currency',
                                  help='Utility field to express amount currency', store=True, readonly=True)
    value = fields.Monetary('Wert', currency_field='currency_id', required=True)

    def _get_default_currency(self):
        for index in self:
            index.currency_id = self._context.get('default_currency_id')

    _sql_constraints = [
        ('unique_year',
         'unique(year)',
         'Eintrag für Jahr existiert bereits')
    ]
