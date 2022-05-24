odoo.define('setu_magic_button.fields_button_script', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var basic_fields = require('web.basic_fields');
var registry = require('web.field_registry');
var core = require('web.core');

var qweb = core.qweb;
var _t = core._t;
var _lt = core._lt;

var SmartButtonWidget = AbstractField.extend({
    className: 'o_favorite',
    events: {
        'click': '_setFavorite'
    },
    supportedFieldTypes: ['integer'],

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * A boolean field is always set since false is a valid value.
     *
     * @override
     */
    isSet: function () {
        return true;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Render favorite icon based on state
     *
     * @override
     * @private
     */
    _render: function () {
        console.log(this.value)
        this.$el.empty().append('<i class="fa fa-info" title="%s" aria-label="%s" role="img"></i>');
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    _setFavorite: function (event) {
        event.preventDefault();
        event.stopPropagation();
        this.do_action({
               type: 'ir.actions.act_window',
                res_model: 'sale.order',
                res_id:7,
                views: [[false, 'form']],
                target: 'new'
            });
    },
});

registry.add('smartbuttonwidget',SmartButtonWidget)

});
