# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Gestion des crédits',
    'version': '1.0',
    'category': 'ARO HR',
    'sequence': 1,
    'summary': 'Module de gestion de crédits',
    'description': """
                Ce module permet de gérer les avantages hors bulletin
                   """,
    'author': 'Solofo',
    'website': 'http://www.aro.mg',
    'depends': ['base', 'hr', 'aro_hr', 'gestion_aro_rh'],
    'data': [
        'views/common_menu.xml',
        'views/hr_employee_advantage_type.xml',
        'views/hr_employee_advantage.xml',
        'views/hr_employee_advantage_line.xml',
        'views/hr_employee_advantage_request.xml',
        'views/hr_employee_inherit.xml',
        'employee_advantage_report.xml',
        'advantage_line_report.xml',
        'data/hr_employee_advantage_type_data.xml',

    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
