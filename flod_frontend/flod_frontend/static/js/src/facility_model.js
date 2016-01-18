var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var Facility = Backbone.Model.extend({
        getUri: function () {
            if (!this.isNew()) {
                return "/facilities/" + this.get("id");
            }
            return null;
        }
    });

    ns.Facilities = Backbone.Collection.extend({
        model: Facility
    });

}(Flod));