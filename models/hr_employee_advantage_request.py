# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models,tools, _
from openerp.exceptions import Warning, ValidationError
import logging
_logger = logging.getLogger(__name__)

class HrEmployeeAdvantageRequest(models.Model):
    _name = 'hr.employee.advantage.request'
    _description = u'Gérer les demandes d avantages'

    def get_emp_id(self):
        emp_obj=self.env['hr.employee']
        _logger.info("\n === Hary = ")
        return emp_obj.search([('user_id','=',self.env.user.id)], limit=1)

    
    employee_id = fields.Many2one('hr.employee.advantage.line', string=u'Employé')
    #advantage_id = fields.Char(related='employee_id.name.name', string='Avantage',readonly=True)
    advantage_id = fields.Many2one(related='employee_id.name',string='Avantage',readonly=True,store=True)
    amount = fields.Float(related='employee_id.amount',string=u'Montant attribué',digits=(8, 2),readonly=True)
    advanced_amount = fields.Float(related='employee_id.advanced_amount',string=u'Montant avancé',digits=(8, 2))
    remaining_amount = fields.Float(related='employee_id.remaining_amount',string='Montant restant',digits=(8, 2))
    date = fields.Datetime(string=u'Envoyé le',required=True)
    cr_number = fields.Char(string=u'Numéro CR')
    request_amount = fields.Float(string=u'Montant demandé',required=True)
    drh_awarded_amount = fields.Float(string=u'Montant accordé')
    observation = fields.Text(string='Motif',required=True)
    drh_observation = fields.Text(string='Observations')
    employee_awarded_amount = fields.Float(string=u'Montant accordé',readonly=True,default=0.0,digits=(8, 2),compute='awarded_amount')
    drh_request_amount = fields.Float(string=u'Montant demandé',readonly=True,default=0.0,digits=(8, 2),compute='validation_request_amount')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('cancel', 'Annulé'),
        ('confirmed', 'Confirmé'),
        ('refuse', 'Refusé'),
        ('validate', 'Validé'),
        ('validate1', 'divRPAS'),
        ('validate2', 'DRH'),
        ('validate3','Comptabilité')], default='draft')
    current_user = fields.Boolean(string='Current user', compute='is_current_user_test',default=True)
    payment_method = fields.Selection(string=u'Paiement souhaité',required=False,selection=[('especes', 'Espèces'), ('cheque', 'Chèque'),('virement','Virement bancaire'),('comte','Compte personnel')])
    #actuel_user = fields.Boolean(string='Utilisateur courant',compute='is_current_user',default=True)
    attachment = fields.Boolean(string=u'Pièces jointes', default=False)
    car_number = fields.Char(string='Immatriculation')
    period = fields.Char(string=u'Période')
    start_counter = fields.Float(string=u'Début du mois',digits=(8, 2))
    end_counter = fields.Float(string=u'Fin du mois',digits=(8, 2))
    traveled_distance = fields.Float(string=u'Kilométrage parcouru',digits=(8,2))
    km_rate = fields.Float(string=u'Taux par km',digits=(8,2))
    car_request_amount = fields.Float(string=u'Montant à rembourser',digits=(8,2))
    car_count = fields.Float(string=u'Compte prêt voiture',digits=(8, 2))
    personal_count = fields.Float(string=u'Compte personnel',digits=(8, 2))
    other_count = fields.Float(string=u'Autres',digits=(8, 2))
    check_out = fields.Float(string=u'Caisse',digits=(8, 2))
    ppe_count = fields.Float(string=u'Compte PPE',digits=(8, 2))
    ph_count = fields.Float(string=u'Compte PH',digits=(8, 2))
    cheque_count = fields.Float(string=u'Chèque',digits=(8, 2))
    total_count = fields.Float(string=u'Total',digits=(8, 2),compute='check_total_amount',readonly=True)
    remaining_imputation = fields.Float(string='Montant restant',compute='check_remaining_imputation',readonly=True)
    #employee_request_id = fields.Many2one(related='employee_id.employee_user_id',string='User request id',store=True)
    emp_id = fields.Many2one('hr.employee',string='Nom Emp',default=get_emp_id)
    user_request_id = fields.Many2one('res.users', string='User ID', related='emp_id.user_id',store=True)
    


    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.emp_id=self.employee_id.officer_id


    #@api.constrains('request_amount')
    #def _check_request_amount(self):
        #for record in self:
            #if record.request_amount > record.remaining_amount:
                #raise exceptions.ValidationError(u"Votre demande de remboursement est supérieure au montant restant autorisé, merci de vérifier")

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def reset_to_draft(self):
        self.state = 'draft'


    @api.multi
    def first_validate(self):
        self.state = 'validate'


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

            if (emp.user_request_id == uid) or (manager == True):
                #if (emp.create_uid == uid) or (manager == True):
                emp.current_user = True
                #else:
                    #emp.current_user=False
                    #raise exceptions.ValidationError(u"Vous n\'êtes pas autorisé à consulter les avantages d une tierce personne")
            else:
                emp.current_user = False
                raise exceptions.ValidationError(u"Vous n\'êtes pas autorisé à consulter les avantages d\' une tierce personne")

    @api.multi
    @api.onchange('employee_id')
    def is_current_user_test(self):
        for emp_request in self:
            uid = self.env.user
            manager=False
            is_in_group = self.env.user.has_group('base.group_hr_manager')
            _logger.info("\n === is_in_group = %s" % is_in_group)
            if is_in_group:
                manager = True
            else:
                manager=False

            if uid == emp_request.user_request_id or manager == True:
                emp_request.current_user = True
                #raise exceptions.ValidationError(u"Vous n\'êtes pas autorisé à consulter les avantages d\' une tierce personne")
            else:
                emp_request.current_user = False
                #raise exceptions.ValidationError(u"Vous n\'êtes pas autorisé à consulter les avantages d\' une tierce personne")

            #if emp_request.employee_id.employee_user_id == emp_request.user_request_id :
            if not emp_request.employee_id.employee_user_id or emp_request.employee_id.employee_user_id == emp_request.user_request_id:
               emp_request.current_user = True
            elif emp_request.employee_id.employee_user_id != emp_request.user_request_id and manager == False :
               #raise exceptions.ValidationError(u"Vous ne pouvez pas saisir les remboursements d\'une tierce personne")
               emp_request.current_user = False

    @api.onchange('drh_awarded_amount')
    def awarded_amount(self):
        for emp_request in self:
            emp_request.employee_awarded_amount = emp_request.drh_awarded_amount

    @api.onchange('request_amount')
    def validation_request_amount(self):
        for emp_request in self:
            emp_request.drh_request_amount = emp_request.request_amount

    #@api.onchange('start_counter','end_counter')
    #def check_distance(self):
        #for emp_request in self:
            #emp_request.traveled_distance=emp_request.end_counter - emp_request.start_counter

    @api.onchange('start_counter','end_counter','km_rate')
    def check_car_request_amount(self):
        for emp_request in self:
            emp_request.car_request_amount=emp_request.traveled_distance * emp_request.km_rate

    @api.onchange('car_count','personal_count','other_count','check_out','ppe_count','ph_count','cheque_count')
    def check_total_amount(self):
        for emp_request in self:
            emp_request.total_count= emp_request.car_count+emp_request.personal_count+emp_request.check_out+emp_request.ppe_count+emp_request.ph_count+emp_request.cheque_count

    @api.onchange('total_count','car_request_amount')
    def check_remaining_imputation(self):
        for emp_request in self:
            emp_request.remaining_imputation=emp_request.car_request_amount - emp_request.total_count
