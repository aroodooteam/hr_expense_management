# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _

class HrEmployeeAdvantage(models.Model):
    _name = 'hr.employee.advantage'
    _description = 'Gestion des avantages'

    #period_id = fields.Many2one('account.period',string=u'Période')
    annee = fields.Char(string=u'Année')
    name = fields.Many2one('hr.employee', string=u'Employé')
    matricule = fields.Char(related="name.matricule", string='Matricule')
    job_id = fields.Char(related="name.job_id.name", string='Job')
    department_id = fields.Char(related="name.department_id.name", string='Service')
    advantage_id = fields.Many2one('hr.employee.advantage.type',string='Avantage')
    amount = fields.Float(string='Montant',digits=(8, 2))
    state = fields.Selection((('add', 'Attribuer'), ('remove', 'Consommer'), ('cancel', 'Annuler')), 'Action')
    ref = fields.Char(string=u'Référence')
    employee_advantage_line_ids = fields.One2many('hr.employee.advantage.line','employee_id',string='Avantages')

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


