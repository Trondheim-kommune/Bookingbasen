var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var MemberOrganisation = Backbone.Model.extend({
        defaults: {
            organisation: {
                name: ""
            }
        }
    });

    var MemberOrganisations = Backbone.Collection.extend({
        model: MemberOrganisation,
        initialize: function (models, options) {
            this.umbrella_organisation_model = options.umbrella_organisation_model;
            this.on("add", this.setUmbrellaOrganisation, this);
        },
        url: function () {
            return "/api/organisations/v1/umbrella_organisations/" + this.umbrella_organisation_model.get('id') + "/organisations/";
        },
        setUmbrellaOrganisation : function(model) {
            model.set({
                "umbrella_organisation_model": this.setUmbrellaOrganisation
            });
        },
        comparator: function (model) {
            return model.get('organisation').name;
        }
    });

    var MemberOrganisationView = Backbone.View.extend({
        events: {
            'click a': 'delete'
        },
        initialize: function (options) {
            this.options = options;
            _.bindAll(this, 'delete', 'error');
            this.model.bind("change", this.render, this);
        },
        render: function () {
            var template = $(this.options.template).html();
            var html = _.template(template, {
                organisation: this.model
            });
            this.$el.html(html);
            return this;
        },
        "delete": function () {
            // Wait for the server to respond before
            // removing the model from the collection.
            this.model.destroy({
                wait: true,
                error: this.error
            });
        },
        error: function (model, xhr) {
            this.$el.find('a').append('<div><span class="label label-important">En feil oppstod</span></div>');
        }
    });

    var MemberOrganisationsView = Backbone.View.extend({
        initialize: function () {
            this.collection.bind("add", this.renderMembers, this);
            this.collection.bind("remove", this.renderMembers, this);
        },
        render: function () {
            var template = $(this.options.template).html();
            var html = _.template(template, {});
            this.$el.html(html);
            this.renderMembers();
            return this;
        },
        renderMembers: function () {
            this.$el.find('#umbrella-organisations').empty();
            _.each(this.collection.models, function (model) {
                this.renderMember(model);
            }, this);
        },
        renderMember: function (model) {
            var view = new MemberOrganisationView({
                model: model,
                template: '#umbrella-member-organisation-template',
                el: '<li>'
            });
            this.$el.find('#umbrella-organisations').append(view.render().$el);
        }
    });

    var AvailableOrganisationView = Backbone.View.extend({
        events: {
            'click a': 'add'
        },
        initialize: function (options) {
            this.options = options;
            _.bindAll(this, 'add', 'error');
        },
        render: function () {
            var template = $(this.options.template).html();
            var html = _.template(template, {
                organisation: this.model
            });
            this.$el.html(html);
            return this;
        },
        add: function () {
            var data = {
                organisation_id: this.model.get("id")
            };
            // Wait for the server before adding
            // the new model to the collection.
            this.options.memberOrganisations.create(data, {
                wait: true,
                error: this.error
            });
        },
        error: function (model, xhr) {
            this.$el.find('a').append('<div><span class="label label-important">En feil oppstod</span></div>');
        }
    });

    var AvailableOrganisationsView = Backbone.View.extend({
        initialize: function (options) {
            this.collection.bind("sync", this.renderOrganisations, this);
            this.options.memberOrganisations.bind("add", this.renderOrganisations, this);
            this.options.memberOrganisations.bind("remove", this.renderOrganisations, this);
        },
        render: function () {
            var template = $(this.options.template).html();
            var html = _.template(template, {});
            this.$el.html(html);
            this.renderOrganisations();
            return this;
        },
        renderOrganisations: function () {
            this.$el.find('#umbrella-organisations').empty();
            _.each(this.collection.models, function (model) {
                this.renderOrganisation(model);
            }, this);
        },
        renderOrganisation: function (model) {
            // Do not show the organisation if
            // it is already a member organisation
            var searchCriteria = {
                "organisation_id": model.get("id")
            };
            if (!this.options.memberOrganisations.findWhere(searchCriteria)) {
                var view = new AvailableOrganisationView({
                    model: model,
                    template: '#umbrella-organisation-template',
                    el: '<li>',
                    memberOrganisations: this.options.memberOrganisations
                });
                this.$el.find('#umbrella-organisations').append(view.render().$el);
            }
        }
    });

    ns.MemberOrganisationsView = Backbone.View.extend({
        events: {
            "click #save": "save",
            "click #searchButton": "fetchAvailableOrganisations"
        },
        initialize: function () {
            _.bindAll(this, "fetchAvailableOrganisations", "showErrorMessage");

            var memberOrganisations = new MemberOrganisations(
                null,
                {
                    umbrella_organisation_model: this.model
                }
            );
            this.memberOrganisationsView = new MemberOrganisationsView({
                collection: memberOrganisations,
                template: "#umbrella-organisations-template"
            });

            if (!this.model.isNew()) {
                memberOrganisations.fetch({
                    error: this.showErrorMessage
                });
            }

            this.availableOrganisations = new ns.Organisations();
            this.availableOrganisationsView = new AvailableOrganisationsView({
                template: "#umbrella-organisations-template",
                collection: this.availableOrganisations,
                memberOrganisations: memberOrganisations
            });
            this.fetchAvailableOrganisations();
        },
        fetchAvailableOrganisations: function () {
            var data = {};
            var name = $("#name", "#available_organisations_filter").val();
            if (_.isString(name) && !_.isEmpty(name))
                data['name'] = name;
            var brregActivityCode = $("#brreg_activity_code", "#available_organisations_filter").val();
            if (_.isString(brregActivityCode) && !_.isEmpty(brregActivityCode))
                data['brreg_activity_code'] = brregActivityCode;
            var flodActivityType = $("#flod_activity_type", "#available_organisations_filter").val();
            if (_.isString(flodActivityType) && !_.isEmpty(flodActivityType))
                data['flod_activity_type'] = flodActivityType;
            this.availableOrganisations.fetch({
                data: data,
                error: this.showErrorMessage
            });
        },
        render: function () {
            this.$el.find("#available-organisations-list").append(this.availableOrganisationsView.render().$el);
            this.$el.find("#member-organisations-list").append(this.memberOrganisationsView.render().$el);
        },
        showErrorMessage: function () {
            this.$el.find("#messages").html(new ns.Notifier().render("En feil oppstod!", "Prøv igjen senere.", "error", 5).$el);
        }
    });

}(Flod));
