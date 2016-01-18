var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";
    ns.Router = Backbone.Router.extend({

        routes: {
            "":      "showHome",
            ":path": "showPath"
        },

        initialize: function (facility) {
            this.facility = facility;
            _.bindAll(this, "showHome", "showPath");
        },

        showHome: function () {
            this.showPath("home");
        },

        showPath: function (path) {

            if (this.facility.isNew()) {
                this.navigate('');
                return;
            }

            $(".tab-pane").removeClass("active");
            $("#" + path).addClass("active");

            $("li.active").removeClass("active");
            $('a[href="#' + path + '"]').parent().addClass("active");

            this.trigger("navigate", path);
        }

    });
}(Flod));