var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var checks = {
        "string": function (value) {
            return typeof value !== 'string' || value.trim().length === 0;
        },
        "nin": function (value) {
            var pattern = /^\d{11}$/;
            return typeof value !== 'string' || value.match(pattern) === null;
        },
        "phone_number": function (value) {
            var pattern = /^\d{8}$/;
            return (typeof value !== 'string' || value.match(pattern) === null) && !_.isUndefined(value);
        }
    };

    var UmbOrgMember = Backbone.Model.extend({
        defaults: {
        },

        required_fields: {
            "first_name": {
                "check": "string",
                "error": "Fornavn er påkrevd."
            },
            "last_name": {
                "check": "string",
                "error": "Etternavn er påkrevd."
            },
            "nin": {
                "check": "nin",
                "error": "Fødselsnummer må bestå av 11 siffer."
            },
            "phone_number": {
                "check": "phone_number",
                "error": "Telefonnummer må være 8 siffer når det spesifiseres."
            }
        },

        url: function () {
            var url = "/api/organisations/v1/umbrella_organisations/" + this.get('umbrella_organisation_model').get('id') + "/persons/";
            if (!this.isNew()) {
                url += this.get("id");
            }
            return url;
        },

        toJSON: function () {
            var data = Backbone.Model.prototype.toJSON.apply(this, arguments);
            return _.omit(data, "umbrella_organisation");
        },

        getData: function () {
            return Backbone.Model.prototype.toJSON.apply(this, arguments);
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
                .map(validateField)
                .flatten()
                .compact()
                .value();

            if (errors.length > 0) {
                return errors;
            }
        }
    });

    ns.UmbOrgMembers = Backbone.Collection.extend({

        model: UmbOrgMember,

        initialize : function (models, options) {
            this.umbrella_organisation_model = options.umbrella_organisation_model;

            this.on("add", this.setUmbrellaOrg, this);
        },

        meta: function (prop, value) {
            if (value === undefined) {
                return this._meta[prop];
            } else {
                this._meta[prop] = value;
            }
        },

        setUmbrellaOrg : function (model) {
            model.set({"umbrella_organisation_model": this.umbrella_organisation_model});
        },

        url: function () {
            return "/api/organisations/v1/umbrella_organisations/" + this.umbrella_organisation_model.get('id') + "/persons/";
        }
    });

    var MemberView = Backbone.View.extend({

        template: $("#member_view_template").html(),

        tagName: "tr",

        events: {
            "click .remove-btn": "removeMember"
        },

        initialize: function () {
            _.bindAll(this, "removeMember");
            this.model.on("destroy", this.remove, this);
            this.model.collection.on('toggleRemove', this.toggleRemove, this);
        },

        render: function (noRemove) {
            var data = this.model.getData();

            //data.noRemove = noRemove;
            this.$el.html(_.template(this.template, {data:data}));
            return this;
        },

        removeMember: function () {
            this.model.destroy({wait: true});
        },

        toggleRemove: function (show) {
            if (show) {
                this.$('.remove-btn').removeClass("hidden");
            } else {
                this.$('.remove-btn').addClass("hidden");
            }
        }
    });

    var Table = Backbone.View.extend({

        tagName: "table",

        className: "table table-condensed",

        initialize: function () {
            this.collection.on("add", this.checkAdd, this);
            this.collection.on("remove", this.checkRemove, this);
        },

        render: function () {
            this.$el.html($("<thead><tr><th>Etternavn</th><th>Fornavn</th><th>Telefon</th><th>E-post-adresse</th><th>Fjern</th></tr></thead>"));
            this.addAll();
            return this;
        },

        addAll: function () {
            this.collection.each(this.checkAdd, this);
        },

        checkRemove: function () {
            if (this.collection.length < 2) {
                this.collection.trigger("toggleRemove", false);
            } else {
                this.collection.trigger("toggleRemove", true);
            }
        },

        checkAdd: function (member) {
            this.addOne(member);

            if (this.collection.length < 2) {
                this.collection.trigger("toggleRemove", false);
            } else {
                this.collection.trigger("toggleRemove", true);
            }

        },

        addOne: function (member) {
            var noRemove = false; // this.collection.length < 2;
            this.$el.append(new MemberView({"model": member}).render(noRemove).$el);
        }
    });

    var AddMemberForm = Backbone.View.extend({

        tagName: "form",

        template: $("#add_member_form_template").html(),

        events: {
            "click #save": "addMember"
        },

        initialize: function (options) {
            this.umbrella_organisation_model = options.umbrella_organisation_model;
            _.bind(this, "addMember");
        },

        render: function () {
            this.$el.html(_.template(this.template));
            return this;
        },

        show: function () {
            this.$("input").val("");
            this.$el.show();
        },

        addMember: function () {
            this.$(".control-group").removeClass("error");
            this.$(".help-inline").text("");
            var first_name = this.$("#first_name").val();
            var last_name = this.$("#last_name").val();
            var nin = this.$("#nin").val();
            var email_address = this.$("#email_address").val();
            var phone_number = this.$("#phone_number").val();

            var user = new UmbOrgMember({
                "last_name": last_name,
                "first_name": first_name,
                "nin": nin,
                "email_address": email_address,
                "phone_number": phone_number,
                "umbrella_organisation_model": this.umbrella_organisation_model
            });

            if (!user.isValid()) {
                this.showErrors(user.validationError);
                return false;
            }
            this.trigger("add", user);
            return false;
        },

        showErrors: function (errors) {
            _.each(errors, function (error) {
                var el = this.$("#" + error.id);
                el.closest(".control-group").addClass("error");
                el.parent().find(".help-inline").text(error.message);
            }, this);
        }
    });

    var MemberAddView = Backbone.View.extend({

        template: $("#add_member_template").html(),

        events: {
            "click #add_member": "showForm"
        },

        initialize: function (options) {
            _.bindAll(this, "showForm", "saved", "error");
            this.umbrella_organisation_model = options.umbrella_organisation_model;

            this.form = new AddMemberForm({"umbrella_organisation_model": this.umbrella_organisation_model});
            this.form.on("add", this.addMember, this);


            this.collection.on("add", this.hideForm, this);
        },

        render: function () {
            this.$el.html(_.template(this.template));
            this.$el.append(this.form.render().$el.hide());
            return this;
        },

        showForm: function () {
            this.$("#add_member").hide();
            this.form.show();
        },

        hideForm: function () {
            this.$("#add_member").show();
            this.form.$el.hide();
        },

        addMember: function (person) {
            person.save(
                {"umbrella_organisation": this.umbrella_organisation_model.get('id')},
                {"success": this.saved, "error": this.error}
            );
        },

        saved: function (person) {
            this.collection.add(person);
            this.$('#user_alert').hide();
            this.$("#errors").empty();
        },

        error: function (model, xhr) {
            var errors = JSON.parse(xhr.responseText);
            if (!errors) {
                return;
            }
            var el = this.$("#errors");
            el.empty();
            _.each(errors["__error__"], function (message) {
                el.append($("<li>").text(message));
            });
            this.$('#user_alert').show();
        }
    });

    var ResponsiblePersonsListView = Backbone.View.extend({

        initialize: function (options) {
            this.table = new Table({"collection": this.collection});
        },

        render: function () {
            this.$el.html(this.table.render().$el);
            return this;
        }

    });

    ns.ResponsiblePersonsView = Backbone.View.extend({

        initialize: function (options) {
            this.umbrella_organisation_model = this.model;

            this.collection = new ns.UmbOrgMembers(null, {"umbrella_organisation_model" : this.umbrella_organisation_model});

            this.responsiblePersonsListView = new ResponsiblePersonsListView({
                "collection": this.collection,
                "el": "#responsible_persons_list",
                "model": this.model
            });
            this.memberAddView = new MemberAddView({
                "collection": this.collection,
                "umbrella_organisation_model": this.umbrella_organisation_model
            });

            // Async, the views will be updated when this returns
            // as they are all listening to this collection!
            if (!this.model.isNew()) {
                this.collection.fetch();
            }
        },

        render: function () {
            this.responsiblePersonsListView.render();
            this.$el.append(this.memberAddView.render().$el);
            return this;
        }

    });

}(Flod));
