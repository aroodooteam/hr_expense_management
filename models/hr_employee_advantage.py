# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from openerp.exceptions import Warning, ValidationError
import logging
_logger = logging.getLogger(__name__)


class HrEmployeeAdvantage(models.Model):
    _name = 'hr.employee.advantage'
    _description = 'Gestion des avantages'

    
    # @api.onchange('name')
    #def get_user_id(self):
    #    uid=self.name.user_id.id
    #    for emp in self:
    #        emp.user_id=uid

    
    #period_id = fields.Many2one('account.period',string=u'Période')
    annee = fields.Char(string=u'Année',required=True)
    name = fields.Many2one('hr.employee', string=u'Employé',required=True)
    matricule = fields.Char(related="name.matricule", string='Matricule')
    job_id = fields.Char(related="name.job_id.name", string='Job')
    department_id = fields.Char(related="name.department_id.name", string='Service')
    advantage_id = fields.Many2one('hr.employee.advantage.type',string='Avantage')
    amount = fields.Float(string='Montant',digits=(8, 2))
    state = fields.Selection((('add', 'Attribuer'), ('remove', 'Consommer'), ('cancel', 'Annuler')), 'Action')
    ref = fields.Char(string=u'Référence')
    employee_advantage_line_ids = fields.One2many('hr.employee.advantage.line','employee_id',string='Avantages')
    #employee_user_id = fields.Integer(string='Employee User id', default=lambda self: self.get_employee_user_id(), readonly=True)
    employee_name_id=fields.Char(compute='get_name_id',string='Name id')
    user_id = fields.Many2one('res.users',string='User', related='name.user_id',store=True)
    current_user_id= fields.Boolean(string='Current user', compute='is_current_user')

    #_sql_constraints = [('name_uniq', 'unique(name)', _('The name must be unique !'))]
    _sql_constraints = [('name_annee_uniq', 'unique(annee,name)', _(u'Vous avez déja saisi les avantages de cet employé !'))]


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
        
            if (emp.user_id == uid) or (manager == True):
                emp.current_user_id = True
            else:
                emp.current_user_id = False
                raise exceptions.ValidationError(u"Vous n\'êtes pas autorisé à consulter les avantages d une tierce personne")

    #@api.onchange('name')
    #def get_employee_user_id(self):
    #    uid=self.name.user_id.id
    #    for emp in self:
    #        emp.employee_user_id=uid
            #return emp.employee_user_id

    @api.multi
    def name_get(self):
        result = super(HrEmployeeAdvantage,self).name_get()
        res = []
        print("result = %s" % result)
        for rec in result:
            # rec = (rec.id,  r_name)
            el_obj = self.browse(rec[0])
            r_name = rec[1] + ' '+ '[' + el_obj.annee + ']'
            res.append((el_obj.id,  r_name))
        return res

    @api.onchange('name')
    def get_name_id(self):
        nid=self.name.id
        for emp in self:
            emp.employee_name_id=nid

