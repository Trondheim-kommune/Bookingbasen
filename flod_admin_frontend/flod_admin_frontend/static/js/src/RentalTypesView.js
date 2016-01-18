var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.RentalTypesView = Backbone.View.extend({
        types: [ "auto_approval_allowed",
                 "single_booking_allowed",
                 "repeating_booking_allowed" ],

        events: {
            "click #save_button": "saveResource"
        },

        initialize: function () {
            this.resource = null;

            this.editable = true;

            if (this.options) {
                if (!_.isNull(this.options.editable) && !_.isUndefined(this.options.editable)) {
                    this.editable = this.options.editable;
                }
            }

            if (this.model.isNew()) {
                this.model.once("sync", this.updateResource, this);
            } else {
                this.updateResource();
            }

        },

        setEditable : function(editable) {
            this.$("input").prop('disabled',!editable);
            this.$("button").prop('disabled',!editable);
        },

        updateResource : function () {
            this.resource = new Flod.Resource({}, { resource_uri: this.model.get("uri") });
            this.formValidation = new ns.FormValidationMixin({el: this.el, model: this.resource});
            this.resource.on("sync", this.updateView, this);
            this.resource.fetch();
        },

        updateView: function () {
            _.each(this.types, function (bookingType) {
                this.$("#" + bookingType).prop("checked", this.resource.get(bookingType));
            }, this);
            this.setEditable(this.editable);
        },

        saveResource: function (event) {
            if (this.resource) {
                event.preventDefault();
                _.each(this.types, function (bookingType) {
                    this.resource.set(bookingType, this.$("#" + bookingType).prop("checked"));
                }, this);

                this.resource.save({}, {
                    success: _.bind(function () {
                        var data = {title: "Suksess!", text: "Leieform ble lagret.", type: ns.Message.MessageType.SUCCESS};
                        var messageModel = new ns.Message(data);
                        this.formValidation.showFormAlert(messageModel);
                    }, this),
                    error: _.bind(function () {
                        var data = {title: "Feil!", text: "Leieform ble ikke lagret. Prøv igjen senere.", type: ns.Message.MessageType.ERROR};
                        var messageModel = new ns.Message(data);
                        this.formValidation.showFormAlert(messageModel);
                    }, this)
                });
            }
        }
    });
}(Flod));
