from odoo import api, SUPERUSER_ID
from odoo.tools import convert_file
from . import models
from . import tools
from . import wizards
import datetime


def import_csv_data(cr, registry):
    """ Import CSV data as it is faster than xml and because we can't use noupdate anymore with
    csv """
    filenames = [
        'data/res.city.csv',
    ]
    for filename in filenames:
        convert_file(
            cr, 'setu_pharma_basic',
            filename, None, mode='init', noupdate=True,
            kind='init'
        )


def init_settings(env):
    """ Make It Enable Product Variant By Default for the Products."""
    for company in env['res.company'].search([]):
        res_config_id = env['res.config.settings'].create({
            'company_id': company.id,
            'group_product_variant': True,
            'days': 5,
            'choice': 'last',
            'start_month': '4'
        })
        # We need to call execute, otherwise the "implied_group" in fields are not processed.
        res_config_id.execute()


def init_fiscal_years_and_periods(env):
    """ Create Current Year's Fiscal Period By Default. """
    fy = env['setu.pharma.fiscalyear'].create({
        "end_month": '3',
        "start_month": '4',
        "end_year": str(datetime.datetime.now().year + 1),
        "start_year": str(datetime.datetime.now().year),
    })
    # We need to call generate_fiscal_periods, otherwise the
    # periods are not generated processed.
    fy._onchange_name()
    fy.generate_fiscal_period()


def init_create_new_default_data(env):
    """ Create Default Headquarter."""
    code = ""
    count = 0
    for company in env['res.company'].search([]):
        count += 1
        division = env['setu.pharma.division'].create({
            'company_id': company.id,
            'name': company.name + " - Generic Division",
            'code': str(count).zfill(5)
        })
        hq = env['setu.pharma.headquarters'].create({
            'company_id': company.id,
            'division_id': division.id,
            'name': company.name + " - Headquarter",
            'city_id':company.city,
            'code': str(count).zfill(5)
        })


def post_init(cr, registry):
    import_csv_data(cr, registry)
    env = api.Environment(cr, SUPERUSER_ID, {})
    init_settings(env)
    init_fiscal_years_and_periods(env)
    # init_create_new_default_data(env)
