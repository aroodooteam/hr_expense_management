# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from openerp.exceptions import ValidationError

class HrEmployeeAdvantageRequest(models.Model):
    _name = 'hr.employee.advantage.request'
    _description = u'Gérer les demandes d avantges'

    employee_id = fields.Many2one('hr.employee.advantage.line', string=u'Employé')
    advantage_id = fields.Char(related='employee_id.name.name', string='Avantage')
    amount = fields.Float(related='employee_id.amount',string=u'Montant attribué',digits=(8, 2),readonly=True)
    advanced_amount = fields.Float(related='employee_id.advanced_amount',string=u'Montant avancé',digits=(8, 2))
    remaining_amount = fields.Float(related='employee_id.remaining_amount',string='Montant restant',digits=(8, 2))
    date = fields.Datetime(string=u'Envoyé le')
    cr_number = fields.Char(string=u'Numéro CR')
    request_amount = fields.Float(string=u'Montant demandé')
    observation = fields.Text(string='Motif')

    @api.constrains('request_amount')
    def _check_request_amount(self):
        for record in self:
            if record.request_amount > record.remaining_amount:
                raise exceptions.ValidationError("Votre demande de remboursement est supérieur au montant restant autorisé, merci de vérifier")


