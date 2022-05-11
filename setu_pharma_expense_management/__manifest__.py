{
    'name': 'Setu Pharma Expense Management',
    'version': '1.0',
    'summary': """
        Manage all pharma related processes in one App.      
    """,
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com/',
    'license': 'Other proprietary',
    'depends': ['hr_expense', 'setu_pharma_basic'],
    'data': [

        # Securities
        'security/ir.model.access.csv',

        # Views
        'views/expense_type.xml',
        'views/expense_configurator.xml',
        'views/distance_range.xml',
        'views/setu_pharma_work_type.xml',
        'views/menu.xml',
        'views/setu_employee_daily_call_view.xml',
        'views/setu_pharma_work_type.xml',
        'views/hr_expense_view.xml'

    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
