var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.Notifier = Backbone.View.extend({

        className: "alert alert-block offset1",

        template: $("#alert_template").html(),

        events: {
            "click .close": "remove"
        },

        initialize: function () {
            _.bindAll(this, "remove");
        },

        render: function (title, text, type, timeout, callback) {
            if (type) {
                this.$el.addClass("alert-" + type);
            }
            if (timeout) {
                setInterval(_.bind(function () {
                    this.remove();
                    if (callback) {
                        callback();
                    }
                }, this), timeout * 1000);
            }
            this.$el.html(_.template(this.template, {"text": text, "title": title}));
            return this;
        }

    });

}(Flod));