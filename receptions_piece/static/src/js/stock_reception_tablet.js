odoo.define('hr_attendance.stock_reception_tablet', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var Session = require('web.session');

var QWeb = core.qweb;

var ReceptionTablet = AbstractAction.extend({

    start: function () {
        var self = this;
        self.session = Session;
        var def = this._rpc({
                model: 'res.company',
                method: 'search_read',
                args: [[['id', '=', this.session.company_id]], ['name']],
            })
            .then(function (receptions){
                self.$el.html(QWeb.render("StockReceptionTablet", {widget: self}));

            });
    },
    
    
});

core.action_registry.add('stock_reception_mode_kiosk', ReceptionTablet);

return KioskMode;

});