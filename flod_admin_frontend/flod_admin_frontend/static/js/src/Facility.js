var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    //lifted from http://stackoverflow.com/questions/1184624/convert-form-data-to-js-object-with-jquery
    $.fn.serializeObject = function () {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function () {
            if (o[this.name] !== undefined) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };

    var checks = {
        "string": function (value) {
            return (_.isUndefined(value) || !value.trim());
        },
        "number_ge0": function (value) {
            return (_.isUndefined(value) || _.isNaN(value) || parseInt(value, 10) < 0);
        },
        "number_gt0": function (value) {
            return (_.isUndefined(value) || _.isNaN(value) || parseInt(value, 10) <= 0);
        },
        "invalid_email": function (value) {
            if (_.isUndefined(value)) {
                return false;
            }
            if (_.isEmpty(value)) {
                return false;
            }
            if (_.isNull(value)) {
                return false;
            }
            if (!_.isString(value)) {
                return true;
            }
            value = value.trim();
            var re = /\S+@\S+\.\S+/;
            return !re.test(value);
        },
        "phone_number": function (value) {
            if (_.isNull(value)) {
                return true;
            }
            var pattern = /^\d{0,8}$/;
            return !_.isString(value) || value.match(pattern) === null;
        },
        "digits": function (value) {
            var pattern = /^\d*$/;
            return !_.isString(value) || value.match(pattern) === null;
        }
    };

    ns.Facility = Backbone.Model.extend({
        urlRoot: "/api/facilities/v1/facilities/",

        defaults: {
            name: "",
            facility_type: null,
            room: '',
            floor: '',
            area: '',
            capacity: '',
            description: '',
            short_description: '',
            link: '',
            unit_type: null,
            unit_name: '',
            department_name: '',
            unit_number: '',
            unit_leader_name: '',
            unit_phone_number: '',
            unit_email_address: '',
            contact_person: null,
            is_deleted: false,
            is_published: false
        },

        required_fields: {
            "name": {
                "check": "string",
                "error": "Du må angi et navn til lokalet."
            },
            "facility_type": {
                "sub": "id",
                "check": "number_gt0",
                "error": "Du må angi en kategori til lokalet."
            },
            "unit_type": {
                "sub": "id",
                "check": "number_gt0",
                "error": "Du må angi en enhetstype for tilhørighet."
            },
            "unit_name": {
                "check": "string",
                "error": "Du må angi et navn på tilhørende enhet."
            },
            "capacity": {
                "check": "number_ge0",
                "error": "Kapasitet må være større eller lik 0 (0 angir ingen begrensning)."
            },
            "unit_email_address": {
                "check": "invalid_email",
                "error": "Du må oppgi en gyldig epost-adresse"
            },
            "area": {
                "check": "number_ge0",
                "error": "Areal må være større eller lik 0"
            },
            "unit_phone_number": {
                "check": "phone_number",
                "error": "Telefonnnummer kan kun bestå av tall (opptil 8)"
            },
            "contact_person": [
                {
                    "sub": "phone_number",
                    "check": "phone_number",
                    "error": "Telefonnnummer kan kun bestå av tall (opptil 8)",
                    "id": "contact_info_phone_number"
                }
            ],
            "unit_number": {
                "check": "digits",
                "error": "Enhetskode kan kun bestå av tall",
                "id": "unit_code"
            }
        },

        initialize: function () {
            this.set('images', new ns.FacilityImages(this.get('images')));
            this.set('documents', new ns.FacilityDocuments(this.get('documents')));
        },

        parse: function (response, options) {
            response.images = this.get('images');
            response.documents = this.get('documents');
            return response;
        },

        validate: function (attrs, options) {

            var validateField = function (validation, field) {
                var value = attrs[field];
                // Determine if we're validating a sub field
                if (_.has(validation, 'sub')) {
                    if (attrs[field]) {
                        value = attrs[field][validation.sub];
                    } else {
                        value = undefined;
                    }
                }
                // Determine if requested check exists
                if (!_.has(checks, validation.check)) {
                    return null;
                }
                // Run the check on the current field value
                var isInvalidValue = checks[validation.check](value);
                if (!isInvalidValue) {
                    return null;
                }
                // Use id property as field name if it's set
                if (_.has(validation, 'id')) {
                    field = validation.id;
                }
                return {
                    id: field,
                    message: validation.error,
                    type: "error"
                };
            };

            var errors = _.chain(this.required_fields)
                .map(function (validation, field) {
                    if (_.isArray(validation)) {
                        return _.map(validation, function (validation) {
                            return validateField(validation, field);
                        });
                    }
                    return validateField(validation, field);
                })
                .flatten()
                .compact()
                .value();

            if (errors.length > 0) {
                return errors;
            }
        },

        getUri: function () {
            if (!this.isNew()) {
                return "/facilities/" + this.get("id");
            }
            return null;
        }
    });

    ns.Facilities = Backbone.Collection.extend({
        model: ns.Facility
    });

    function fixInt(value) {
        if (value.trim() === "") {
            value = 0;
        }
        return parseInt(value, 10);
    }

    ns.FacilityView = Backbone.View.extend({

        tagName: "clearfix",

        initialize: function () {
            _.bindAll(this, "save", "delete", "published", "getModelValues", "toggleSport", "toggleBand", "saveSucceess", "saveError", "deleteSucceess", "deleteError", "publishedSucceess", "publishedError");

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

        events: {
            "click #save": "save",
            "click #delete": "delete",
            "click #published": "published",
            "click #suitability_sport": "toggleSport",
            "click #suitability_band": "toggleBand"
        },

        render: function () {
            var data = this.model.toJSON();
            data.facility_types = this.options.facility_types;
            data.unit_types = this.options.unit_types;

            this.$el.html(_.template($("#facility_template").html(), data));

            // Set the amenities after templating
            this.setDict("amenities", data.amenities);
            this.setDict("accessibility", data.accessibility);
            this.setDict("equipment", data.equipment);
            this.setDict("suitability", data.suitability);
            this.setDict("facilitators", data.facilitators);
            this.toggleSport();
            this.toggleBand();
            return this;
        },

        toggleSport: function () {
            var isChecked = this.$("#suitability_sport").prop("checked");
            if (isChecked) {
                this.$("#sport_equipment").show();
            } else {
                this.$("#sport_equipment").hide();
                this.$("#sport_equipment input[type=checkbox]").attr('checked',
                    false);
            }
        },

        toggleBand: function () {
            var isChecked = this.$("#suitability_band").prop("checked");
            if (isChecked) {
                this.$("#band_equipment").show();
            } else {
                this.$("#band_equipment").hide();
                this.$("#band_equipment input[type=checkbox]").attr('checked',
                    false);
            }
        },

        setDict: function (prefix, data) {
            _.each(data, function (value, key) {
                this.$("#" + prefix + "_" + key).prop(
                    'checked',
                    value === "on" || value === "True"
                );
            }, this);
        },

        extractDict: function (prefix, data) {
            var dict = {};
            _.each(data, function (value, key) {
                var sub = key.substring(0, prefix.length);
                if (sub === prefix) {
                    dict[key.slice(prefix.length)] = value;
                    delete data[key];
                }
            });
            return dict;
        },

        getModelValues: function () {
            var data = this.$("form").serializeObject();

            //make a dict of contact person (shares prefix)
            data.contact_person = this.extractDict("contact_person_", data);

            // Extract the amenities (they share a prefix)
            data.amenities = this.extractDict("amenities_", data);
            data.accessibility = this.extractDict("accessibility_", data);
            data.equipment = this.extractDict("equipment_", data);
            data.suitability = this.extractDict("suitability_", data);
            data.facilitators = this.extractDict("facilitators_", data);

            //fix facility and unit type (they should be dicts)
            data.facility_type = {"id": data.facility_type};
            data.unit_type = {"id": data.unit_type};

            //parse ints as ints
            data.area = fixInt(data.area);
            data.capacity = fixInt(data.capacity);
            return data;
        },

        save: function () {
            var data = this.getModelValues();
            this.model.set(data);
            this.model.save(data, {
                success: this.saveSucceess,
                error: this.saveError
            });
        },
        'delete': function (e) {
            var self = this;
            // If yes button is clicked in the delete dialog
            $('#btnYes').click(function () {
                self.model.destroy({
                    success: self.deleteSucceess,
                    error: self.deleteError
                });
            });
        },
        published: function (e) {
            var data = this.model.toJSON();
            var is_published = !this.model.get("is_published");
            this.model.set("is_published", is_published);
            data.is_published = is_published;
            this.model.save(data, {
                success: this.publishedSucceess,
                error: this.publishedError
            });
        },

        publishedSucceess: function (model, response) {
            window.location.href = "/resource/" + model.get("id");
        },

        publishedError: function (model, response) {
            var data = {
                title: "Feil!",
                text: "Lokalet ble ikke lagret. Prøv igjen senere.",
                type: ns.Message.MessageType.ERROR
            };
            var messageModel = new ns.Message(data);
            this.formValidation.showFormAlert(messageModel);
        },

        deleteSucceess: function (model, response) {
            window.location.href = "/resources";
        },

        deleteError: function (model, response) {

        },

        saveSucceess: function () {
            var data = {
                title: "Suksess!",
                text: "Lokalet ble lagret.",
                type: ns.Message.MessageType.SUCCESS
            };
            var messageModel = new ns.Message(data);
            this.formValidation.showFormAlert(messageModel);
        },

        saveError: function (model, response) {
            var error = JSON.parse(response.responseText);
            var errorString = error["__error__"].join(", ");

            this.$el.prepend(
                new ns.Notifier().render(
                    "Lokalet ble ikke lagret. Prøv igjen senere.",
                    error.message || errorString,
                    "error"
                ).$el
            );
            $(".alert").removeClass("offset1");
        }
    });

}(Flod));
