# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _

class HrEmployeeAdvantageType(models.Model):
    _name = 'hr.employee.advantage.type'
    _description = 'Liste des types d avantage'

    name = fields.Char(string='Description')
    rate = fields.Float(string='Taux', digits=(6,2))
    code = fields.Char(string='Code')