var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.OrganisationEmailView = Backbone.View.extend({

        events: {
            "click .btn": "contact"
        },

        el: "#emails",

        initialize: function () {
            _.bindAll(this, "contact");
        },

        contact: function () {
            this.modal = new Flod.Modal({
                "template_data": {
                    "title": "Kontakt aktører",
                    "btn_cancel_txt": "Lukk",
                    "emails": this.emails || this.options.emails
                }
            });
            this.modal.render();

            var textarea = this.modal.$el.find("textarea");
            this.modal.$el.on('shown', function () {
                if (textarea) {
                    textarea.select();
                }
            });
            this.modal.show();
        },

        render: function () {
            return this;
        }
    });

    ns.createOrganisationEmailView = function (options) {
        return new ns.OrganisationEmailView(options);
    };
})(Flod);
