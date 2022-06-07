# -*- coding: utf-8 -*-
{
    'name': 'Setu Pharma Employee Incentive',
    'version': '1.0',
    'summary': """
        Manage all pharma Sales Targets related processes in one App.      
    """,
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com/',
    'license': 'Other proprietary',
    'depends': ['hr', 'sale_stock', 'sale_management', 'approvals', 'crm', 'sale',
                'product_expiry','base_address_city', 'setu_pharma_basic'],
    'data': [
        # Securities
        'security/ir.model.access.csv',
        # Views
        'views/setu_pharma_sales_target_view.xml',
        'views/setu_pharma_sales_target_products.xml',
        'views/setu_pharma_incentive_structure.xml',
        'views/setu_pharma_sales_range.xml',
        'views/setu_pharma_sales_mxmlenu_extended.',
    ],
    'installable': True,
    'auto_install': False,
}
