var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.UmbrellaInformationView = Backbone.View.extend({

        className: "clearfix",

        events: {
            "click #save": "save",
            "click #delete": "delete"
        },

        initialize: function () {
            _.bindAll(this, "save", "delete", "getModelValues", "saveSuccess", "saveError", "deleteSuccess", "deleteError");

            if (this.options) {
                if (!_.isNull(this.options.editable) && !_.isUndefined(this.options.editable)) {
                    this.editable = this.options.editable;
                }
            }

            this.formValidation = new ns.FormValidationMixin({
                el: this.el,
                model: this.model
            });
        },

        render: function () {
            var data = this.model.toJSON();
            this.$el.html(_.template($("#umbrella_information_template").html(), data));
            if (this.model.isNew()) {
                this.$el.find("#delete").addClass("disabled").removeAttr("data-toggle");
            }
            return this;
        },

        getModelValues: function () {
            return this.$("form").serializeObject();
        },

        save: function () {
            var data = this.getModelValues();
            this.model.set(data);
            this.model.save(data, {
                success: this.saveSuccess,
                error: this.saveError
            });
        },

        saveSuccess: function () {
            var data = {
                title: "Suksess!",
                text: "Paraplyorganisasjonen ble lagret.",
                type: ns.Message.MessageType.SUCCESS
            };
            var messageModel = new ns.Message(data);
            this.formValidation.showFormAlert(messageModel);
            if (!this.model.isNew()) {
                this.$el.find("#delete").removeClass("disabled").attr("data-toggle","modal");
            }
        },

        saveError: function (model, response) {
            var error_text = 'Paraplyorganisasjonen ble ikke lagret. Årsak: ';

            try {
                error_text += JSON.parse(response.responseText).__error__;
            } catch (err) {
                // ignore
                error_text += "Ukjent feil oppstod.";
            }

            var data = {
                title: "Feil!",
                text: error_text,
                type: ns.Message.MessageType.ERROR
            };
            var messageModel = new ns.Message(data);
            this.formValidation.showFormAlert(messageModel);
        },

        "delete": function (e) {
            var self = this;
            // If yes button is clicked in the delete dialog
            $('#btnYes').click(function () {
                self.model.destroy({
                    success: self.deleteSuccess,
                    error: self.deleteError
                });
            });
        },

        deleteSuccess: function (model, response) {
            window.location.href = "/umbrella_organisations";
        },

        deleteError: function (model, response) {

        }
    });

}(Flod));
