from odoo import models, fields


class AssessmentIndex(models.Model):
    _name = 'assessment.index'
    _description = 'Index'
    _order = 'name desc'

    name = fields.Integer('Jahr', required=True)  # TODO: format without thousand seperator
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id,
                                  help='Utility field to express amount currency', store=True, readonly=True)
    value = fields.Monetary('Wert', currency_field='currency_id', required=True)

    _sql_constraints = [
        ('unique_year',
         'unique(name)',
         'Eintrag für Jahr existiert bereits')
    ]