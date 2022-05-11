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


def post_init(cr, registry):
    import_csv_data(cr, registry)
