# -*- coding: utf-8 -*-




{
    'name': 'SD HR holidays',
    'version': '18.0.1.0.1',
    'category': 'Human Resources',
    'summary': """ It works as base module for HR extended 1 modules """,
    'author': 'Arash Homayounfar',
    'company': 'Giladoo',
    'maintainer': 'Giladoo',
    'website': "https://www.giladoo.com/sdhr",
    'installable': True,
    'auto_install': False,
    'application': False,
    'depends': ['hr', 'sd_projects' ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_holidays.xml',
        'views/mission_detail.xml',
        'views/mission_report.xml',
        'views/views.xml',
    ],
    'assets':{
        'web.assets_backend':[
          'sd_hr_holidays/static/src/components/**/*.js',
          'sd_hr_holidays/static/src/components/**/*.xml',
          'sd_hr_holidays/static/src/components/**/*.scss',
        ],
    },

    'license': 'LGPL-3',
}
