{
    'name': 'Setu Pharma',
    'version': '1.0',
    'summary': """
        Manage all pharma related processes in one App.      
    """,
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com/',
    'license': 'Other proprietary',
    'depends': ['hr', 'sale_stock', 'sale_management', 'approvals', 'crm', 'sale'],
    'data': [
        # Datas
        'data/speciality_res_partner_category_data.xml',
        'data/setu_pharma_work_type_data.xml',
        'data/approval_categories/pharma_approval_category_data.xml',
        'data/approval_categories/pharma_approval_tour_plan_category.xml',
        'data/approval_categories/pharma_approval_general_category.xml',
        'data/uom_data.xml',
        # 'data/setu.pharma.city.csv',
        # 'data/fiscal_year.xml',

        # Sequences
        'data/ir_sequences_setu_pharma.xml',

        # Securities
        'security/ir.model.access.csv',
        # 'security/res_groups.xml',
        'security/record_rules.xml',

        # Views
        'views/ir_actions_inherited.xml',
        'views/area.xml',
        'views/city.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/product_product.xml',
        'views/fiscal_year.xml',
        'views/fiscal_period.xml',
        'views/city_distance.xml',
        'views/designation.xml',
        'views/employee.xml',
        'views/setu_pharma_headquarters.xml',
        'views/stockist_monthly_statement_view.xml',
        'views/res_partner_doctor.xml',
        'views/res_partner_stockist.xml',
        'views/res_partner_retailer.xml',
        'views/stock_location.xml',
        'views/stock_warehouse.xml',
        'views/doctor_support.xml',
        'views/doctor_support_line.xml',
        'views/employee_daily_call_report.xml',
        'views/employee_daily_call_report_line.xml',
        'views/employee_sampling_and_gift_reporting.xml',
        'views/employee_sampling_and_gift_reporting_line.xml',
        'views/personal_order_booking.xml',
        'views/personal_order_booking_line.xml',
        'views/stockist_statement.xml',
        'views/stockist_statement_line.xml',
        'views/tour_plan.xml',
        'views/tour_plan_line.xml',
        'views/speciality_res_partner_category.xml',
        'views/division.xml',
        'views/res_users.xml',
        'views/res_company.xml',
        'views/setu_pharma_work_type.xml',
        'views/approval_request_view.xml',
        # Make this Menu File in Last Order
        'views/menu.xml',
        'views/setu_pharma_ex_headquater.xml',

        # Wizards
        'wizards/tp_line_selection_wizard.xml',
        'wizards/dcr_line_product_selection_wizard.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'setu_pharma_basic/static/src/*',
            'setu_pharma_basic/static/src/webclient/**/*'
        ],
        'web.assets_qweb': [
            'setu_pharma_basic/static/src/webclient/switch_division_menu/*.xml',
        ],
    },
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'post_init',
}
