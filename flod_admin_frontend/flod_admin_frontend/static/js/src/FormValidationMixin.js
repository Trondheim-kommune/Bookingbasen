var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    /**
     * If you are not able to set model at time of allocation, you can set it later
     * on this same view with <code>setModel(model)</code>
     *
     * model    : the model that we validate and get error objects from.
     * el       : the element where the error message will be _prepended_ to.
     *
     */
    ns.FormValidationMixin = Backbone.View.extend({

        initialize: function () {
            this.messageView = null;
            if (!_.isUndefined(this.model)) {
                this.setUpModelListeners();
            }
        },

        setModel : function (model) {
            if (!_.isNull(this.model) && !_.isUndefined(this.model)) {
                this.tearDownListeners();
                this.model = null;
            }

            this.model = model;
            this.setUpModelListeners();
        },

        tearDownListeners : function () {
            this.stopListening(this.model);
        },

        setUpModelListeners : function () {
            this.listenTo(this.model, 'invalid', this.render); // on validation error
            this.listenTo(this.model, 'change',  this.render); // on success
            this.listenTo(this.model, 'request', this.render); // on server response error
        },

        /**
         * ns.Message
         */
        showFormAlert : function (messageModel) {
            this.clearFormAlert();

            this.messageView = new ns.MessageView({model: messageModel});
            this.$el.prepend(this.messageView.render().el);
        },

        clearFormAlert : function () {
            // Top message - form alert
            if (this.messageView) {
                this.messageView.close();
                this.messageView = null;
            }
        },

        clearValidationAlerts : function () {
            // inline messages related to form data
            this.$el.find('div').removeClass("error control-group");
            this.$el.find('div span.help-inline').remove();
        },

        showValidationAlerts : function () {
            this.clearFormAlert();
            this.clearValidationAlerts();

            if (this.model.validationError) {
                var data = {title: "Feil i skjemadata!",
                    text: "Det er en eller flere feil i skjemaet. Felter med feil er markert med rødt.",
                    type: ns.Message.MessageType.ERROR};

                var messageModel = new ns.Message(data);
                this.showFormAlert(messageModel);

                _.each(this.model.validationError, function (item) {
                    this.$('#' + item.id).parent('div').addClass("error control-group");
                    var elem;
                    if (this.options.parent) {
                        elem = this.options.parent;
                    } else {
                        elem = this.$('#' + item.id).parent('div');
                    }
                    elem.append("<span class='help-inline text-error'>" + item.message + "</span>");
                }, this);
            }
        },

        render : function () {
            this.showValidationAlerts();
            return this;
        }
    });

}(Flod));
