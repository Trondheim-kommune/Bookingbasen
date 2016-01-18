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
            return typeof value !== 'string' || value.match(pattern) === null;
        }
    };

    ns.UmbrellaOrganisation = Backbone.Model.extend({
        urlRoot: "/api/organisations/v1/umbrella_organisations/",

        defaults : {
            name: "",
            responsible_persons: []
        },

        required_fields: {
            "name": {
                "check": "string",
                "error": "Du må angi et navn til paraplyorganisasjonen."
            }
        },

        initialize: function () {
            //this.set('organisations', new ns.MemberOrganisations(this.get('organisations')));
        },

        parse : function (response, options) {

            // We need to only update the organisation collection values
            //this.get('organisations').set(response['organisations']);
            //delete response['organisations'];

            return response;
        },

        validate : function (attrs, options) {

            var validateField = function (validation, field) {
                var value = attrs[field];
                // Determine if we're validating a sub field
                if (_.has(validation, 'sub')) {
                    value = attrs[field][validation.sub];
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
                return "/umbrella_organisations/" + this.get("id");
            }
            return null;
        }
    });

    ns.UmbrellaOrganisations = Backbone.Collection.extend({
        model: ns.UmbrellaOrganisation
    });

}(Flod));
