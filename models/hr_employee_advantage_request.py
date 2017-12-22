# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models,tools, _
from openerp.exceptions import Warning, ValidationError
import logging
_logger = logging.getLogger(__name__)

class HrEmployeeAdvantageRequest(models.Model):
    _name = 'hr.employee.advantage.request'
    _description = u'Gérer les demandes d avantages'

    user_request_id = fields.Many2one('res.users', string='User ID', default=lambda self: self.env.user)
    employee_id = fields.Many2one('hr.employee.advantage.line', string=u'Employé')
    advantage_id = fields.Char(related='employee_id.name.name', string='Avantage')
    amount = fields.Float(related='employee_id.amount',string=u'Montant attribué',digits=(8, 2),readonly=True)
    advanced_amount = fields.Float(related='employee_id.advanced_amount',string=u'Montant avancé',digits=(8, 2))
    remaining_amount = fields.Float(related='employee_id.remaining_amount',string='Montant restant',digits=(8, 2))
    date = fields.Datetime(string=u'Envoyé le')
    cr_number = fields.Char(string=u'Numéro CR')
    request_amount = fields.Float(string=u'Montant demandé')
    observation = fields.Text(string='Motif')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('cancel', 'Annulé'),
        ('confirmed', 'Confirmé'),
        ('refuse', 'Refusé'),
        ('validate1', 'divRPAS'),
        ('validate2', 'DRH'),
        ('validate3','Comptabilité')], default='draft')
    current_user = fields.Boolean(string='Current user', compute='is_current_user')
   

    @api.constrains('request_amount')
    def _check_request_amount(self):
        for record in self:
            if record.request_amount > record.remaining_amount:
                raise exceptions.ValidationError(u"Votre demande de remboursement est supérieur au montant restant autorisé, merci de vérifier")

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def reset_to_draft(self):
        self.state = 'draft'

    @api.multi
    def validate_dRPAS(self):
        self.state = 'validate1'

    @api.multi
    def validate_DRH(self):
        self.state = 'validate2'

    @api.multi
    def validate_CPTE(self):
        self.state = 'validate3'

    @api.multi
    def check_employee_request(self):
                
        if self.env.user.id == self.employee_id.employee_user_id :
            raise Warning("Vrai")
        else:
            raise Warning("Faux")

    @api.multi
    def is_current_user(self):
        for emp in self:
            uid = self.env.user
            manager=False
            is_in_group = self.env.user.has_group('base.group_hr_manager')
            _logger.info("\n === is_in_group = %s" % is_in_group)
            if is_in_group:
                manager = True
            else:
                manager=False
        
            if (emp.create_uid == uid) or (manager == True):
                emp.current_user = True
            else:
                emp.current_user = False
                raise exceptions.ValidationError(u"Vous n êtes pas autorisé à consulter les avantages d une tierce personne")


