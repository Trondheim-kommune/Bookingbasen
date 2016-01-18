var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var Address = ns.Address = Backbone.Model.extend({
        defaults: {
            address_line: null,
            postal_city: null,
            postal_code: null
        },

        toJSON: function () {
            if (_.isEmpty(this.get("address_line")) && _.isEmpty(this.get("postal_city")) && _.isEmpty(this.get("postal_code"))) {
                return null;
            }
            return Backbone.Model.prototype.toJSON.apply(this, arguments);
        },

        toDisplay: function () {
            return Backbone.Model.prototype.toJSON.apply(this, arguments);
        }
    });


    ns.BrregOrganisation = Backbone.Model.extend({
        url: function () {
            return "/api/organisations/v1/brreg/enhet?orgnr=" + this.get("org_number");
        }
    });

    function nullOrEmptyString(value) {
        return (!value || value === '');
    }

    ns.Organisation = Backbone.Model.extend({

        defaults: {
            org_number: null,
            name: null,
            postal_address: null,
            business_address: null,
            num_members: null,
            num_members_b20: null,
            description: null,
            phone_number: null,
            telefax_number: null,
            email_address: null,
            local_email_address: null,
            area: 0,
            type_organisation: null,
            flod_activity_type: null,
            brreg_activity_code: null,
            type_activity: null,
            account_number: null,
            registered_tkn: false,
            relevant_tkn: false,
            update_brreg: false,
            is_public: false
        },

        brreg_fields: [
            "name", "phone_number", "telefax_number",
            "email_address", "postal_address", "business_address"
        ],

        initialize: function () {
            var tilholdssted_address = this.get("tilholdssted_address");
            if (tilholdssted_address) {
                this.set("tilholdssted_address", new Address(tilholdssted_address));
            }
            var postal_address = this.get("postal_address");
            if (postal_address) {
                this.set("postal_address", new Address(postal_address));
            }
            var business_address = this.get("business_address");
            if (business_address) {
                this.set("business_address", new Address(business_address));
            }
        },

        set: function (key, val, options) {
            if (_.isString(key)) {
                if ((key === "postal_address" || key === "business_address" || key === "tilholdssted_address") && !(val instanceof Address)) {
                    val = new Address(val);
                }
            }
            return Backbone.Model.prototype.set.apply(this, [key, val, options]);
        },

        url: function () {
            var url = "/api/organisations/v1/organisations/";
            if (!this.isNew()) {
                url += this.get("id");
            }
            return url;
        },


        validate: function (attributes) {
            if (this.has('org_number')) {
                return;
            }

            var errors = {};
            if (nullOrEmptyString(attributes.name)) {
                errors.name = "Du må oppgi et navn";
            }

            if (!_.isEmpty(errors)) {
                return errors;
            }
        },

        toJSON: function () {
            var data = {
                "id": this.get("id"),
                "org_number": this.get("org_number"),
                "area": this.get("area"),
                "recruitment_area": this.get("recruitment_area"),
                "brreg_activity_code": this.get("brreg_activity_code"),
                "flod_activity_type": this.get("flod_activity_type"),
                "num_members": this.get("num_members"),
                "num_members_b20": this.get("num_members_b20"),
                "registered_tkn": this.get("registered_tkn"),
                "relevant_tkn": this.get("relevant_tkn"),
                "description": this.get("description"),
                "user": this.get("user"),
                "update_brreg": this.get("update_brreg"),
                "is_public": this.get("is_public")
            };

            if (!this.has("org_nr")) {
                data.name = this.get("name");
                if (this.has('tilholdssted_address')) {
                    data.tilholdssted_address = this.get("tilholdssted_address").toJSON();
                }
                if (this.has('postal_address')) {
                    data.postal_address = this.get("postal_address").toJSON();
                }
                if (this.has('business_address')) {
                    data.business_address = this.get("business_address").toJSON();
                }
                data.phone_number = this.get("phone_number");
                data.telefax_number = this.get("telefax_number");
                data.email_address = this.get("email_address");
                data.local_email_address = this.get("local_email_address");
            }
            return data;
        },

        getContactPerson: function () {
            return _.find(this.get("persons"), function (person) {
                return (person.org_roles.indexOf("Kontaktperson") !== -1);
            });
        },

        toDisplay: function () {
            var data = Backbone.Model.prototype.toJSON.apply(this, arguments);
            if (this.has("tilholdssted_address")) {
                data.tilholdssted_address = this.get("tilholdssted_address").toDisplay();
            } else {
                data.tilholdssted_address = false;
            }
            if (this.has("postal_address")) {
                data.postal_address = this.get("postal_address").toDisplay();
            } else {
                data.postal_address = false;
            }
            if (this.has("business_address")) {
                data.business_address = this.get("business_address").toDisplay();
            } else {
                data.business_address = false;
            }
            var contactPerson = this.getContactPerson();
            if (contactPerson) {
                data.contact_person = contactPerson.first_name + " " +
                    contactPerson.last_name;
            } else {
                data.contact_person = "-";
            }
            return data;
        },

        isBrregField: function (key) {
            return (this.brreg_fields.indexOf(key) !== -1);
        }
    });

    ns.Organisations = Backbone.Collection.extend({
        url: "/api/organisations/v1/organisations/",
        model: ns.Organisation,
        comparator: function(model) {
            return model.get('name');
        }
    });
}(Flod));
