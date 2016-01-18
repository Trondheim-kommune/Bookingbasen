var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.Settings = Backbone.Model.extend({
        url: "/api/booking/v1/adm_leieform/"
    });

}(Flod));