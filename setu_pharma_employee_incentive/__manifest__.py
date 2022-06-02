# -*- coding: utf-8 -*-
{
    'name': "Setu Pharma Employee Incentive",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Setu Consulting Services Pvt. Ltd.",
    'website': "https://www.setuconsulting.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management', 'setu_pharma_basic', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/setu_pharma_sales_target_view.xml',
        'views/setu_pharma_sales_target_products.xml',
        'views/setu_pharma_incentive_structure.xml',
        'views/setu_pharma_sales_range.xml',
        'views/setu_pharma_sales_menu_extended.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
