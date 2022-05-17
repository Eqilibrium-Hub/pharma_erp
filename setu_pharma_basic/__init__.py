from odoo import api, SUPERUSER_ID
from odoo.tools import convert_file
from . import models
from . import tools
from . import wizards


def import_csv_data(cr, registry):
    """ Import CSV data as it is faster than xml and because we can't use noupdate anymore with
    csv """
    filenames = [
        'data/setu.pharma.city.csv',
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
            'group_product_variant': True
        })
        # We need to call execute, otherwise the "implied_group" in fields are not processed.
        res_config_id.execute()

def post_init(cr, registry):
    import_csv_data(cr, registry)
    env = api.Environment(cr, SUPERUSER_ID, {})
    init_settings(env)
