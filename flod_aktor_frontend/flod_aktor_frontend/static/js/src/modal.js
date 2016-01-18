var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.Modal = Backbone.View.extend({

        template: $("#modal_template").html(),

        className: "modal hide fade",

        events: {
            "click .btn-primary": "submit",
            "click .btn-inverse": "hide"
        },

        initialize: function () {
            _.bindAll(this, "submit");
        },

        render: function () {
            this.$el.html(_.template(this.template, this.options.template_data));
            $(document.body).append(this.$el);
            this.$el.on('hide', _.bind(this.remove, this));
            return this;
        },

        show: function () {
            this.$el.modal('show');
        },

        hide: function () {
            this.$el.modal('hide');
            this.trigger("cancel");
        },

        submit: function () {
            this.trigger("submit");
        }
    });
}(Flod));