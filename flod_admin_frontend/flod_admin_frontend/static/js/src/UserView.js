var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var RemoveCredentialToUserModel = Backbone.Model.extend({

        url: function () {
            return "/api/users/v1/users/" + this.get('user_id') + "/credentials/" + this.get('credential_id');
        }
    });

    var UserView = Backbone.View.extend({
        template: $("#user_template").html(),

        events: {
            "click .remove": "remove"
        },

        tagName: 'tr',

        initialize : function () {
            _.bindAll(this, "deleteSuccess", "deleteError");

            this.editable = this.options.editable;

            if (this.options.facility_id) {
                this.facility_id = this.options.facility_id;
            }

            this.collection = this.options.collection;

        },

        remove : function () {

            if (this.facility_id) {
                var credentialModel = new RemoveCredentialToUserModel({
                    'credential_id': 'CAN_EDIT_FACILITY_' + this.facility_id,
                    'user_id': this.model.get('id'),
                    'id':  this.model.get('id')
                });
                var self = this;
                credentialModel.destroy({
                    success: self.deleteSuccess,
                    error: self.deleteError
                });
            }
        },

        deleteSuccess : function (model) {

            this.collection.forEach(function (element) {
                if (element.get('id') === model.get('id')) {
                    this.collection.remove(element);
                    $("#message").html(
                        new ns.Notifier().render(
                            "Suksess",
                            "Tilknytningen ble fjernet.",
                            "success",
                            10
                        ).$el
                    );
                    return;
                }
            }, this);
        },

        deleteError : function (model, xhr, options) {
            $("#message").html(
                new ns.Notifier().render(
                    "Feil",
                    "En ukjent feil oppstod. Vennligst prøv igjen senere.",
                    "error",
                    10
                ).$el
            );
        },

        render: function () {
            var outputHtml = _.template(this.template, this.model.toJSON());
            this.$el.html(outputHtml);
            return this;
        }

    });

    ns.UserCollectionView = Backbone.View.extend({
        tagName: 'div',

        initialize: function () {
            _.bindAll(this, 'render');

            this.editable = true;
            this.facility_id = null;

            if (this.options) {
                if (!_.isNull(this.options.editable) && !_.isUndefined(this.options.editable)) {
                    this.editable = this.options.editable;
                }
                if (!_.isNull(this.options.facility_id) && !_.isUndefined(this.options.facility_id)) {
                    this.facility_id = this.options.facility_id;
                }
            }

            this.collection.bind('add', this.render);
            this.collection.bind('remove', this.render);
        },

        render: function () {
            this.$el.empty();

            var elements = this.collection.map(function (user) {
                var userView = new UserView({
                    model: user,
                    editable : this.editable,
                    facility_id : this.facility_id,
                    collection: this.collection
                });
                return userView.render().$el;
            }, this);

            this.$el.append(elements);

            return this;
        }
    });


}(Flod));
