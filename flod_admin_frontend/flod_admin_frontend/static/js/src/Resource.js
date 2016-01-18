var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.Resource = Backbone.Model.extend({

        url: function () {
            return "/api/booking/v1/resources" + this.resource_uri;
        },

        initialize: function (attributes, options) {
            options = options || {};
            if (options.resource_uri) {
                this.resource_uri = options.resource_uri;
            }
        }
    });
}(Flod));
