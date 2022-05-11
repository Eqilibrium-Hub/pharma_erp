odoo.define('setu_pharma_basic.Session', function (require) {
"use strict";

var session = require('web.Session');

session.include ({
    setDivisions: function (main_division_id, division_ids) {
        var hash = $.bbq.getState();
        hash.divids = division_ids.sort(function(a, b) {
            if (a === main_division_id) {
                return -1;
            } else if (b === main_division_id) {
                return 1;
            } else {
                return a - b;
            }
        }).join(',');
        utils.set_cookie('divids', hash.divids || String(main_division_id));
        $.bbq.pushState({'divids': hash.divids}, 0);
        location.reload();
    },
})
})