# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from openerp.exceptions import Warning, ValidationError
import logging
_logger = logging.getLogger(__name__)


class HrEmployeeAdvantageLine(models.Model):
    _name = 'hr.employee.advantage.line'
    _description = u'Détail des avantages attribués'

    contract_id = fields.Many2one('hr.contract',string='Contrat')
    adv_contract_id = fields.Many2one('hr.contract',string='Contrat')
    employee_id = fields.Many2one('hr.employee.advantage', string=u'Employé')
    annee = fields.Char(related='employee_id.annee',string=u'Année',readonly=True, store=True)
    name = fields.Many2one('hr.employee.advantage.type',string='Avantage')
    matricule=fields.Char(related='employee_id.name.matricule', string='Matricule', readonly=True)
    amount = fields.Float(string=u'Montant attribué',digits=(8, 2))
    advanced_amount = fields.Float(string=u'Montant avancé',digits=(8, 2),compute='get_advanced_amount')
    #advanced_amount_corrected = fields.Float(string=u'Montant avancé corrigé',digits=(8, 2),compute='get_advanced_amount')
    remaining_amount = fields.Float(string='Montant restant',digits=(8, 2),compute='get_remaining_amount',store=True)
    remaining_balance = fields.Float(string=u'Montant restant',digits=(8, 2),compute='get_remaining_balance',store=True)
    current_balance = fields.Float(string=u'Montant restant',digits=(8, 2),store=True)
    monthly_amount = fields.Float(string='Montant mensuel',readonly=False,default=0.0, store=True,digits=(8, 2), compute='_onchange_amount')
    state = fields.Selection((('add', 'Attribuer'), ('remove', 'Consommer'), ('cancel', 'Annuler')), 'Action')
    ref = fields.Char(string=u'Référence')
    employee_advantage_request_ids = fields.One2many('hr.employee.advantage.request','employee_id', string=u'Avantage demandé')
    employee_user_id = fields.Many2one(related='employee_id.user_id', string='User id',store=True)
    current_user= fields.Boolean(string='Current user', compute='is_current_user')
    officer_id = fields.Many2one(related='employee_id.name',string='Employee ID',store=True)
    user_request_id = fields.Integer(string='User request id', compute='get_user_request_id',store=True)
    #emp_id = fields.Many2one('hr.employee',string='Nom Emp',default=get_emp_id)
    #test_employee_id = fields.Integer(string='Employee ID')


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
    @api.depends('employee_advantage_request_ids.drh_awarded_amount')
    def get_advanced_amount(self):
        for montant in self:
            emp_request=len(montant.employee_advantage_request_ids)
            count=0
            i=0
            while i < emp_request:
                for request in montant.employee_advantage_request_ids:
                    #count =count +request.request_amount
                    count+= request.drh_awarded_amount
                    i=i+1
                    montant.advanced_amount=count
                    #montant.advanced_amount_corrected=montant.advanced_amount


    @api.multi
    def get_balance(self):
        for montant in self:
            if montant.advanced_amount != 0:
                montant.current_balance=montant.amount-montant.advanced_amount
            else:
                montant.current_balance=montant.amount

    @api.depends('amount','advanced_amount')
    @api.multi
    def get_remaining_amount(self):
        for montant in self:
            if montant.advanced_amount != 0:
                montant.remaining_amount=montant.amount-montant.advanced_amount
            else:
                montant.remaining_amount=montant.amount

    @api.depends('amount','advanced_amount')
    @api.multi
    def get_remaining_balance(self):
        for montant in self:
            if montant.advanced_amount != 0:
                montant.remaining_balance=montant.amount-montant.advanced_amount
            else:
                montant.remaining_balance=montant.amount


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

    @api.depends('amount')
    def _onchange_amount(self):
        for montant in self:
            montant.monthly_amount = montant.amount/12


    #@api.multi
    @api.depends('officer_id')
    def get_user_request_id (self):
        for emp_request in self:
            emp_request.user_request_id = emp_request.officer_id


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Rajout des avantages hors bulletin dans la table contrat'

    employee_advantage_line_ids = fields.One2many('hr.employee.advantage.line','adv_contract_id',string='Avantage hors bulletin')
    fonction_mensuelle = fields.Float(string='Fonction mensuelle', store=True)
    representation_mensuelle = fields.Float(string='Representation mensuelle',readonly=True,default=0.0, store=True,digits=(8, 2))
    voiture_mensuelle = fields.Float(string='Voiture mensuelle',readonly=True,default=0.0, store=True,digits=(8, 2))
    telephone_mensuelle = fields.Float(string=u'Téléphone mensuelle',readonly=True,default=0.0, store=True,digits=(8, 2))

    @api.onchange('employee_advantage_line_ids')
    def update_get_monthly_amount(self):
        _logger.info('\n=== ctx = %s ===\n' % self._context)
        _logger.info('\n=== line_ids = %s ===\n' % self.employee_advantage_line_ids)
        ctt_obj = self.browse([self._context.get('default_adv_contract_id')])
        _logger.info('\n=== ctt_obj = %s ===\n' % ctt_obj)
        vals = {}
        for advantage_line_id in ctt_obj.employee_advantage_line_ids:
            _logger.info("\n === FONCTION = %s" %advantage_line_id.adv_contract_id)
            code_fonction=advantage_line_id.name.search([('code','=','F')]).id
            code_representation=advantage_line_id.name.search([('code','=','R')]).id
            code_telephone=advantage_line_id.name.search([('code','=','T')]).id
            code_voiture=advantage_line_id.name.search([('code','=','V')]).id
            if advantage_line_id.name.id == code_fonction:
                vals['fonction_mensuelle'] = advantage_line_id.monthly_amount
                #self.fonction_mensuelle=advantage_line_id.monthly_amount
                ctt_obj.write(vals)
            elif advantage_line_id.name.id == code_representation:
                 vals['representation_mensuelle'] = advantage_line_id.monthly_amount
                #self.representation_mensuelle=advantage_line_id.monthly_amount
                 ctt_obj.write(vals)
            elif advantage_line_id.name.id == code_telephone:
                 vals['telephone_mensuelle'] = advantage_line_id.monthly_amount
                #self.representation_mensuelle=advantage_line_id.monthly_amount
                 ctt_obj.write(vals)
            elif advantage_line_id.name.id == code_voiture:
                 vals['voiture_mensuelle'] = advantage_line_id.monthly_amount
                #self.representation_mensuelle=advantage_line_id.monthly_amount
                 ctt_obj.write(vals)
            _logger.info('\n=== vals = %s => %s ===\n' % (vals, self))
            #ctt_obj.write(vals)





