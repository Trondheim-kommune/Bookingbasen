var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.Rammetid = Backbone.Model.extend({
        url: function () {
            var base = "/api/booking/v1/rammetid/";
            if (!this.isNew()) {
                base += this.get("id");
            }
            return base;
        },
        getSlots: function () {
            return _.map(this.get("rammetid_slots"), function (slot) {
                return _.clone(slot);
            }, this);
        }
    });

}(Flod));
