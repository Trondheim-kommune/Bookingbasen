var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.Person = Backbone.Model.extend({

        url: function () {
            return "/api/organisations/v1/persons/" + this.get("id");
        },

        defaults: {
            "first_name": "",
            "last_name": "",
            "email": "",
            "phone": ""
        },

        validate : function (attrs, options) {

            var checks = {
                "first_name": "Du må oppgi fornavn.",
                "last_name": "Du må oppgi etternavn.",
                "email_address": "Du må oppgi e-post.",
                "phone_number": "Du må angi et telefonnummer."
            };

            var errors = _.compact(_.map(checks, function (errorMessage, id) {
                if (!attrs[id]) {
                    return {
                        id: id,
                        message: errorMessage,
                        type: "error"
                    };
                }
            }));

            if (attrs.phone_number) {
                var pattern = /^[\d\s]+$/;
                if (attrs.phone_number.match(pattern) === null) {
                    errors.push({
                        id: "phone_number",
                        message: "Telefonnummeret kan kun inneholde tall.",
                        type: "error"
                    });
                }
            }

            if (errors.length) {
                return errors;
            }

        },

        toJSON: function (options) {
            var attrs = Backbone.Model.prototype.toJSON.apply(this, options);
            // Remove spaces from phone number
            if (attrs.phone_number) {
                attrs.phone_number = attrs.phone_number.replace(/\s+/g, '');
            }
            return attrs;
        }
    });

    ns.ProfileFormView = Backbone.View.extend({

        template: $("#profile_form_template").html(),

        tagName: "form",

        className: "form-horizontal",

        events: {
            "submit": "submit"
        },

        initialize: function () {
            _.bindAll(this, "submit", "saved",
                "clearAlerts", "invalidData", "notSaved");

            this.listenTo(this.model, "invalid", this.invalidData);
        },

        clearAlerts : function () {
            this.$el.find('div').removeClass("error");
            this.$el.find('div span.help-inline').remove();
        },

        notSaved : function (model, response) {
            var error = JSON.parse(response.responseText);
            _.each(error, this.addError, this);

            var data = {
                title: "Feil!",
                text: "Din profil ble ikke lagret. Prøv igjen senere.",
                type: "error"
            };

            this.$el.append(
                new ns.Notifier().render(
                    data.title,
                    data.text,
                    data.type
                ).$el
            );
        },

        addObjError: function (error, key) {
            _.each(error, function (error, key) {
                this.addError(error, key);
            }, this);
        },

        addError: function (error, key) {
            if (_.isObject(error)) {
                this.addObjError(error, key);
            } else {
                var elem;
                if (this.options.parent) {
                    elem = this.options.parent;
                } else {
                    elem = this.$('#id_' + key).parent('div');
                }
                if (elem.length === 0) {
                    elem = this.$('div').first();
                }
                elem.addClass("error control-group");
                elem.append("<span class='help-inline'>" + error + "</span>");
            }
        },

        invalidData : function () {
            if (this.model.validationError) {

                var data = {
                    title: "Feil i skjemadata!",
                    text: "Det er en eller flere feil i skjemaet. Felter med feil er markert med rødt.",
                    type: "error"
                };

                this.$el.append(
                    new ns.Notifier().render(
                        data.title,
                        data.text,
                        data.type
                    ).$el
                );

                _.each(this.model.validationError, function (item) {
                    this.showInlineError(item.id, item.message);
                }, this);
            }
        },

        showInlineError: function (id, message) {
            this.$('#id_' + id).parent('div').addClass(
                "error control-group"
            );
            this.$('#id_' + id).parent('div').append(
                "<span class='help-inline'>" + message + "</span>"
            );
        },

        render: function () {

            var data = {
                "first_name": this.model.get("first_name"),
                "last_name": this.model.get("last_name"),
                "email_address": this.model.get("email_address"),
                "phone_number": this.model.get("phone_number")
            };

            this.$el.html(_.template(this.template, data));
            return this;
        },

        submit: function (event) {
            event.preventDefault();

            this.clearAlerts();

            var form_data = this.$el.serializeObject();

            var data = {
                "first_name": form_data.first_name,
                "last_name": form_data.last_name,
                "email_address": form_data.email_address,
                "phone_number": form_data.phone_number
            };

            this.model.save(
                data,
                {"success": this.saved, "error" : this.notSaved}
            );
            return false;
        },

        saved: function () {
            if (this.model.get("status") === "registered") {
                this.$el.append(
                    new ns.Notifier().render(
                        "Brukerdetaljer lagret!",
                        "Dine detaljer er nå oppdatert!",
                        "success"
                    ).$el
                );
            } else { //atlefren: this should not happen??
                this.$el.append(
                    new ns.Notifier().render(
                        "Det skjedde en feil.",
                        "Dataene ble ikke registrert. Se over at alle dataene er riktige.",
                        "error"
                    ).$el
                );
            }
        }
    });

}(Flod));
