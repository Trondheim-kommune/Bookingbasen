var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.OrganisationInfoFormView = Backbone.View.extend({

        template: $("#org_info_template").html(),
        user_mode: "",

        showDelete: false,

        events: {
            "click #save_org": "showConfirmation",
            "click #updateBrreg": "updateBrreg",
            "click #delete": "deleteOrganisation"
        },

        initialize: function () {
            _.bindAll(this, "saveOrganisation", "updateBrreg", "updateOrganisation");

            this.model.set("user_mode",this.options.user_mode);
        },

        render: function () {
            this.undelegateEvents();
            var data = this.model.toDisplay();
            data.districts = _.reject(this.options.districts, function (disitrict) {
                return disitrict.all === true;
            });

            data.recruiting_districts = _.reject(this.options.recruiting_districts, function (disitrict) {
                return disitrict.all === true;
            });

            if (this.model.has("brreg_activity_code")) {
                var activityCodes = this.options.brreg_activity_codes.getByCodes(
                    this.model.get("brreg_activity_code")
                );

                data.brreg_activity_code = activityCodes.toDisplay();
                data.activities = activityCodes.getActivityTypes().toJSON();
            } else {
                data.activities = [];
            }

            data.fromBrreg = this.model.has("org_number");
            data.showDelete = this.showDelete;
            data.showUpdateBtn = (!this.model.isNew() &&
            this.model.has("org_number"));
            data.isNew = this.model.isNew();

            this.$el.html(_.template(this.template, data));
            this.activitytypechooser = new ns.ActivityTypeChooser({
                "el": this.$("#activity_chooser"),
                "activities": data.activities
            });

            if (this.model.has("flod_activity_type")) {
                this.activitytypechooser.selectActivities(
                    this.model.get("flod_activity_type")
                );
            }

            if (this.model.has("area")) {
                this.$("#id_area").val(this.model.get("area"));
            }

            if (this.model.has("recruitment_area")) {
                this.$("#id_recruitment_area").val(this.model.get("recruitment_area"));
            }

            this.$('#id_num_members').attr("readonly", this.options.user_mode !== 'admin');
            this.$('#id_num_members_b20').attr("readonly", this.options.user_mode !== 'admin');
            this.delegateEvents();
            return this;
        },

        clear: function () {
            this.$el.html("");
        },

        updateBrreg: function () {
            this.result = new ns.BrregOrganisation({
                "org_number": this.model.get("org_number")
            });
            this.result.fetch({"success": this.updateOrganisation});

            var el = $("<div>Henter data</div>").addClass("searching");
            this.$("#updateBrreg").after(el);
            this.$("#updateBrreg").remove();
        },

        updateOrganisation: function (brregDataModel) {
            this.getFormData();
            _.each(brregDataModel.attributes, function (value, key) {
                if (this.model.isBrregField(key)) {
                    this.model.set(key, value);
                }
            }, this);

            this.model.set("update_brreg", true);
            this.render();
        },

        getFormData: function () {
            var data = this.$("form").serializeObject();
            data.registered_tkn = (data.registered_tkn === "on");
            data.is_public = (data.is_public === "on");

            var flod_activity_type = this.activitytypechooser.collection.map(
                function (activity) {
                    return activity.get("id");
                }
            );

            var tilholdssted_address = new ns.Address({
                address_line: data.tilholdssted_address_address_line,
                postal_city: data.tilholdssted_address_postal_city,
                postal_code: data.tilholdssted_address_postal_code
            });

            this.model.set({
                org_number: this.model.get("org_number"),
                name: data.name,
                num_members: parseInt(data.num_members, 10),
                num_members_b20: parseInt(data.num_members_b20, 10),
                description: data.description,
                phone_number: data.phone_number,
                telefax_number: data.telefax_number,
                email_address: data.email_address,
                local_email_address: data.local_email_address,
                area: data.area,
                recruitment_area: data.recruitment_area,
                type_organisation: data.type_organisation,
                flod_activity_type: flod_activity_type,
                registered_tkn: data.registered_tkn,
                is_public: data.is_public,
                tilholdssted_address: tilholdssted_address
            });

            if (this.options.user_mode === 'admin'){
                data.relevant_tkn = (data.relevant_tkn === "on");
                this.model.set({relevant_tkn: data.relevant_tkn});
            }

            if (!this.model.has("org_number")) {

                var postal_address = new ns.Address({
                    address_line: data.postal_address_address_line,
                    postal_city: data.postal_address_postal_city,
                    postal_code: data.postal_address_postal_code
                });

                var business_address = new ns.Address({
                    address_line: data.business_address_address_line,
                    postal_city: data.business_address_postal_city,
                    postal_code: data.business_address_postal_code
                });

                this.model.set({
                    postal_address: postal_address,
                    business_address: business_address
                });
            }
        },

        deleteOrganisation: function (e) {
            var self = this;
            // If yes button is clicked in the delete dialog
            $('#btnYes').click(function () {
                self.model.destroy({
                    success: self.deleteSucceess,
                    error: self.deleteError
                });
            });
        },

        deleteSucceess: function (model, response) {
            window.location.href = "/organisations";
        },

        deleteError: function (model, response) {

        },

        showConfirmation: function () {
            this.clearValidationAlerts();
            this.getFormData();
            if (!this.model.isValid()) {
                this.showErrors();
                return;
            }
            // Skip confirmation for ad-hoc orgs and existing orgs
            var is_adhoc = this.model.get('org_number') === null;
            if (is_adhoc || !this.model.isNew() || this.options.user_mode === 'admin') {
                this.saveOrganisation();
                return;
            }
            this.modal = new Flod.Modal({
                "template_data": {
                    "name": this.model.get('name')
                }
            });
            this.modal.render();
            this.modal.on("cancel", this.saveOrganisation, this);
            this.modal.on("submit", function () {
                this.modal.$el.modal("hide");
                this.model.set("is_public", true);
                this.saveOrganisation();
            }, this);
            this.modal.show();
        },

        saveOrganisation: function () {
            var person = window.loggedInPerson;
            if (this.model.isValid()) {
                var el = $("<div id='saveSpinner'>Lagrer</div>").addClass("searching");
                this.$("#save_org").after(el);
                this.$("#save_org").hide();

                this.model.save(
                    {"user": person !== undefined ? person.toJSON() : {}},
                    {
                        "success": _.bind(this.orgSaved, this),
                        "error": _.bind(this.saveFailed, this)
                    }
                );
            } else {
                this.showErrors();
            }
        },

        showErrors: function () {
            _.each(this.model.validationError, function (error, key) {
                if (_.isObject(this.model.validationError[key])) {
                    for (var child_key in this.model.validationError[key]) {
                        this.showError(this.model.validationError[key][child_key], key + "_" + child_key)
                    }
                } else {
                    this.showError(error, key)
                }
            }, this);
        },

        showError: function(error, key){
            this.$('#id_' + key).parent('div').addClass("error control-group");
            var elem;
            if (this.options.parent) {
                elem = this.options.parent;
            } else {
                elem = this.$('#id_' + key).parent('div');
            }
            elem.append("<span class='help-inline text-error'>" + error + "</span>");
        },

        clearValidationAlerts: function () {
            // inline messages related to form data
            this.$el.find('div').removeClass("error control-group");
            this.$el.find('div span.help-inline').remove();
        },

        orgSaved: function (organisation) {
            this.model.initialize();
            this.model.set("update_brreg", false);

            this.$("#save_org").show();
            this.$("#saveSpinner").remove();
            this.saveCallback(organisation);
        },

        saveFailed: function (model, response) {
            this.$("#saveSpinner").remove();
            this.$("#save_org").show();

            var error = JSON.parse(response.responseText).__error__;

            if (!_.isArray(error)) {
                model.validationError = error;
                this.showErrors();
            } else {
                this.$el.append(new ns.Notifier().render(
                    error.join(", "),
                    "",
                    "error"
                ).$el);
            }
        },

        saveCallback: function (organisation) {
            this.$el.append(new ns.Notifier().render(
                "Organisasjonen ble lagret",
                "",
                "success"
            ).$el);
        }
    });
}(Flod));
