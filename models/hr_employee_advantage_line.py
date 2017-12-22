# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from openerp.exceptions import Warning, ValidationError
import logging
_logger = logging.getLogger(__name__)

class HrEmployeeAdvantageLine(models.Model):
    _name = 'hr.employee.advantage.line'
    _description = u'Détail des avantages attribués'

    employee_id = fields.Many2one('hr.employee.advantage', string=u'Employé')
    annee = fields.Char(related='employee_id.annee',string=u'Année',readonly=True, store=True)
    name = fields.Many2one('hr.employee.advantage.type',string='Avantage')
    amount = fields.Float(string=u'Montant attribué',digits=(8, 2))
    advanced_amount = fields.Float(string=u'Montant avancé',digits=(8, 2),compute='get_advanced_amount')
    remaining_amount = fields.Float(string='Montant restant',digits=(8, 2),compute='get_remaining_amount')
    state = fields.Selection((('add', 'Attribuer'), ('remove', 'Consommer'), ('cancel', 'Annuler')), 'Action')
    ref = fields.Char(string=u'Référence')
    employee_advantage_request_ids = fields.One2many('hr.employee.advantage.request','employee_id', string=u'Avantage demandé')
    employee_user_id = fields.Many2one(related='employee_id.user_id', string='User id')
    current_user= fields.Boolean(string='Current user', compute='is_current_user')

    @api.multi
    def name_get(self):
        result = super(HrEmployeeAdvantageLine,self).name_get()
        res = []
        print("result = %s" % result)
        for rec in result:
            # rec = (rec.id,  r_name)
            el_obj = self.browse(rec[0])
            #r_name = rec[1] + ' '+ '[' + el_obj.annee + ']'+ ' '+ '[' + el_obj.employee_id.name.name + ']'
            r_name = '[' + el_obj.employee_id.name.name + ']'+' '+ rec[1] + ' '+ '[' + el_obj.annee + ']'
            res.append((el_obj.id,  r_name))
        return res

    @api.multi
    def get_advanced_amount(self):
        for montant in self:
            emp_request=len(montant.employee_advantage_request_ids)
            count=0
            i=0
            while i < emp_request:
                for request in montant.employee_advantage_request_ids:
                    count =count +request.request_amount
                    i=i+1
                    montant.advanced_amount=count
        #montant.remaining_amount=montant.amount-montant.advanced_amount
        #montant.remaining_amount="50"

    @api.onchange('amount','employee_advantage_request_ids.advanced_amount')
    def get_remaining_amount(self):
        for montant in self:
            for request in montant.employee_advantage_request_ids:
                montant.remaining_amount=montant.amount-montant.advanced_amount

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
        
            if (emp.employee_user_id == uid) or (manager == True):
                emp.current_user = True
            else:
                emp.current_user = False
                raise exceptions.ValidationError(u"Vous n êtes pas autorisé à consulter les avantages d une tierce personne")