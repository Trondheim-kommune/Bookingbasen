var Flod = window.Flod || {};

(function (ns, undefined) {
    'use strict';

    var AddCredentialToUserModel = Backbone.Model.extend({

        url: function () {
            return "/api/users/v1/users/" + this.get('user_id') + "/credentials/" + this.get('credential_id');
        }
    });

    ns.AddCredentialToUserView = Backbone.View.extend({
        events: {
            'click #save': 'save',
            'change #bruker_private_id': 'reset_control_group_class'
        },

        initialize: function (options) {
            _.bindAll(this, 'save', 'save_success', 'save_error', 'updateAdminFilter');

            if (this.options) {
                if (!_.isNull(this.options.editable) && !_.isUndefined(this.options.editable)) {
                    this.editable = this.options.editable;
                }
            }

            this.facility = options.facility;
            this.model = null; // user model to be added as admin
            this.addCredentialsToUserModel = null;
            this.currentAdminCollection = options.currentAdminCollection;

            if (this.facility.isNew()) {
                this.listenToOnce(this.facility, "sync", this.updateAdminFilter);
            } else {
                this.updateAdminFilter();
            }
        },

        updateAdminFilter : function () {
            this.currentAdminCollection.setFilters(
                {
                    "credential_id": "CAN_EDIT_FACILITY_" + this.facility.get("id"),
                    "resource_id": this.facility.get("id")
                }
            );
            this.currentAdminCollection.fetch();
        },

        save_success: function () {
            var self = this;
            $("#message").html(
                new ns.Notifier().render(
                    "Suksess",
                    "Brukeren " + self.model.get('profile').first_name + " (" + self.model.get('private_id') + ") ble lagt til som admin for lokalet.",
                    "success",
                    10
                ).$el
            );

            this.currentAdminCollection.add(this.model);
            this.addCredentialsToUserModel = null;
            this.model = null;
        },

        save_error: function () {
            $("#message").html(
                new ns.Notifier().render(
                    "Feil",
                    "En ukjent feil oppstod. Vennligst prøv igjen senere.",
                    "error",
                    10
                ).$el
            );
            this.addCredentialsToUserModel = null;
            this.model = null;
        },

        save: function () {

            if (this.model) {
                this.addCredentialsToUserModel = new AddCredentialToUserModel({
                    user_id: this.model.get('id'),
                    credential_id: "CAN_EDIT_FACILITY_" + this.facility.get("id")
                });

                this.addCredentialsToUserModel.save({},
                    {
                        success: this.save_success,
                        error: this.save_error
                    });
            } else {
                this.save_error();
            }
        }

    });
}(Flod));
