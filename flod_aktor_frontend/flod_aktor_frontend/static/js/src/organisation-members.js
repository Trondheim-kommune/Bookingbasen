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

    var OrgMember = Backbone.Model.extend({


        defaults: {
            from_brreg: false
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
            var url = "/api/organisations/v1/organisations/" + this.get("organisation") + "/persons/";
            if (!this.isNew()) {
                url += this.get("id");
            }
            return url;
        },

        toJSON: function () {
            var data = Backbone.Model.prototype.toJSON.apply(this, arguments);
            return _.omit(data, "organisation", "from_brreg");
        },

        getData: function () {
            return Backbone.Model.prototype.toJSON.apply(this, arguments);
        },

        validate: function (attrs, options) {
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

    ns.OrgMembers = Backbone.Collection.extend({

        model: OrgMember,

        setOrgId: function (orgId) {
            this.each(function (member) {
                member.set({"organisation": orgId});
            });
        }
    });

    var Person = Backbone.Model.extend({
        url: function () {
            return "/api/organisations/v1/persons/" + this.get("id");
        }
    });

    var EditMemberView = Backbone.View.extend({
        template: $("#edit_member_template").html(),

        initialize: function (options) {
            this.render();
        },

        render: function () {
            this.$el.html(_.template(this.template)(this.model.toJSON()));
            return this;
        },

        getModel: function () {
            return {'email_address': this.$el.find("#id_email_address").val(), 'phone_number': this.$el.find("#id_phone_number").val()};
        },

        showError: function (error) {

            _.each(error, this.addError, this);

            this.$("#validation").empty();

            this.$("#validation").prepend(
                new ns.Notifier().render(
                    "Feil!",
                    "En feil oppstod under redigering.",
                    "error"
                ).$el
            );
            $(".alert").removeClass("offset1");
        },


        addObjError: function (error, key) {
            _.each(error, function (error, key) {
                this.addError(error, key);
            }, this);
        },

        addError: function (error, key) {
            if (_.isObject(error)) {
                this.addObjError(error, key);
            } else {
                var elem;
                if (this.options.parent) {
                    elem = this.options.parent;
                } else {
                    elem = this.$('#id_' + key).parent('div');
                }
                if (elem.length === 0) {
                    elem = this.$('div').first();
                }
                elem.addClass("error control-group");
                elem.append("<span class='help-inline text-error control-label'>" + error + "</span>");
            }
        },

        clearValidationAlerts: function () {
            this.$el.find('div').removeClass("error control-group");
            this.$el.find('div span.help-inline').remove();
        }
    });

    var MemberView = Backbone.View.extend({

        template: $("#member_view_template").html(),

        tagName: "tr",

        events: {
            "click .remove-btn": "removeMember",
            "click .edit-btn": "editMember"
        },

        initialize: function () {
            _.bindAll(this, "removeMember");
            this.model.set("role", _.pluck(this.model.get("roles"), 'role').join(', '));

            this.model.on("destroy", this.remove, this);
            this.model.collection.on('toggleRemove', this.toggleRemove, this);
        },

        render: function (noRemove) {
            var data = this.model.getData();
            data.noRemove = noRemove;
            this.$el.html(_.template(this.template, data));
            return this;
        },

        removeMember: function () {
            this.model.destroy({wait: true});
        },

        editMember: function () {
            this.modal = new Flod.Modal({
                "template_data": {
                    "title": "Redigere medlemsdata",
                    "btn_txt": "Lagre",
                    "btn_cancel_txt": "Avbryt"
                }
            });

            this.modal.render();

            var editMemberView = new EditMemberView({
                model: this.model,
                el: this.modal.$(".modal-body")
            });

            this.modal.on("submit", _.bind(function () {
                var newModel = editMemberView.getModel();
                var person = new Person({
                    'id': this.model.get('id'),
                    'phone_number': newModel.phone_number,
                    'email_address': newModel.email_address
                });

                var self = this;
                editMemberView.clearValidationAlerts();

                person.save(
                    {},
                    {
                        'success': function () {
                            self.memberEdited();
                            self.model.set("email_address", newModel.email_address);
                            self.model.set("phone_number", newModel.phone_number);
                        },
                        'error': function (model, xhr, options) {
                            var error = JSON.parse(xhr.responseText);
                            editMemberView.showError(error);
                        }
                    }
                );
            }, this));

            this.modal.show();
        },

        memberEdited: function () {
            window.location.reload();
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
            var headers = "<tr><th>Etternavn</th><th>Fornavn</th><th>Telefon</th><th>E-post-adresse</th><th>Rolle</th>";
            if (this.options.user_mode === 'soker' || this.options.user_mode === 'admin') {
                headers += "<th>Fjern</th>";
            }
            if (this.options.user_mode === 'admin') {
                headers += "<th>Redigere</th>";
            }
            headers += "</tr>";
            this.$el.append($(headers));

            this.addAll();
            return this;
        },

        addAll: function () {
            this.collection.each(this.addOne, this);
        },

        checkRemove: function () {
            if (this.collection.length < 2) {
                this.collection.trigger("toggleRemove", false);
            } else {
                this.collection.trigger("toggleRemove", true);
            }
        },

        checkAdd: function (member) {
            if (this.collection.length < 2) {
                this.collection.trigger("toggleRemove", false);
            } else {
                this.collection.trigger("toggleRemove", true);
            }
            this.addOne(member);
        },

        addOne: function (member) {
            var noRemove = this.collection.length < 2;
            this.$el.append(new MemberView({"model": member}).render(noRemove).$el);
        }
    });

    var AddMemberForm = Backbone.View.extend({

        tagName: "form",

        template: $("#add_member_form_template").html(),

        events: {
            "submit": "addMember"
        },

        initialize: function () {
            _.bind(this, "addMember");
        },

        render: function () {
            this.$el.append(_.template(this.template));
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

            var user = new OrgMember({
                "last_name": last_name,
                "first_name": first_name,
                "nin": nin,
                "email_address": email_address,
                "phone_number": phone_number
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
            this.form = new AddMemberForm();
            this.form.on("add", this.addMember, this);
            this.org_id = options.org_id;

            this.collection.on("add", this.hideForm, this);
        },

        render: function () {
            this.$el.append(_.template(this.template));
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

        addMember: function (user) {
            user.save({"organisation": this.org_id}, {"validate": false, "success": this.saved, "error": this.error});
        },

        saved: function (user) {
            this.collection.add(user);
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

    ns.MemberListView = Backbone.View.extend({

        initialize: function (options) {
            this.table = new Table({"collection": this.collection, "user_mode": options.user_mode});
            this.collection.setOrgId(options.org_id);
            this.memberAddView = new MemberAddView({"collection": this.collection, "org_id": options.org_id});
        },

        render: function () {
            this.$el.append(this.table.render().$el);
            if (this.options.user_mode === 'soker' || this.options.user_mode === 'admin') {
                this.$el.append(this.memberAddView.render().$el);
            }
            return this;
        }

    });

}(Flod));
