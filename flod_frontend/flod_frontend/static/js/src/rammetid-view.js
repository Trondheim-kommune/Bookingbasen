var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var colors = [
        '#C00000', '#996633', '#00C000', '#C0FFC0', '#0000C0',
        '#404000', '#C0C000', '#008080', '#00FFFF', '#C000C0',
        '#C05800', '#663399', '#990033', '#FF0099', '#FFC0C0'
    ];

    var LegendView = Backbone.View.extend({

        tagName: "table",

        className: "table table-bordered legend",

        render: function () {

            var template = "<tr>" +
                "<td class='other' style='background-color: <%= color %>;'></td>" +
                "<td><%= name %></td>" +
                "</tr>";

            var rows = this.collection.map(function (org) {
                return $(_.template(
                    template,
                    {color: org.get('color'), name: org.get('name')}
                ));
            });
            this.$el.append(rows);
            return this;
        }

    });

    var DropdownView = Backbone.View.extend({
        template: $("#dropdown_template").html(),

        events: {
            "change ": "change"
        },

        initialize: function (options) {
            this.title = options.title;
            _.bindAll(this, "change");
            this.collection.on('reset', this.render, this);
        },

        render: function () {
            var data = {
                title: this.title,
                values: this.collection.map(function (model) {
                    return {id: model.get("id") || model.cid, name: model.get("name")};
                })
            };
            this.$el.html(_.template(this.template, data));
            return this;
        },

        change: function () {
            var model_id = this.$("select").val();
            var model = this.collection.get(model_id);
            this.trigger("modelSelected", model);
        }
    });

    var Period = Backbone.Model.extend({

        initialize: function () {
            var start_date = moment(this.get('start_date'), 'YYYY-MM-DD');
            var end_date = moment(this.get('end_date'), 'YYYY-MM-DD');
            var name = start_date.format('DD-MMM-YYYY') + " - " + end_date.format('DD-MMM-YYYY');
            this.set("name", name);
        },

        getDates: function () {
            return {
                "start_date": this.get("start_date"),
                "end_date": this.get("end_date")
            };
        }
    });

    var Periods = Backbone.Collection.extend({
        model: Period,
        initialize: function (models, options) {
            options || (options = {});
            this.umbrellaOrganisationUri = options.umbrellaOrganisationUri;
            this.resourceUri = options.resourceUri;
        },
        url: function () {
            var url = "/api/booking/v1/rammetid/?only_periods";
            if (this.umbrellaOrganisationUri) {
                url += "&umbrella_organisation_uri=" + this.umbrellaOrganisationUri;
            }
            if (this.resourceUri) {
                url += "&resource_uri=" + this.resourceUri;
            }
            return url;
        },
        setResource: function (resource) {
            this.resourceUri = resource.get('uri');
        }
    });

    ns.UmbrellaOrganisation = Backbone.Model.extend({});

    ns.MemberOrganisation = Backbone.Model.extend({
        parse: function (response) {
            response.name = response.organisation.name;
            return response;
        }
    });

    ns.MemberOrganisations = Backbone.Collection.extend({
        model: ns.MemberOrganisation
    });

    var RammetidResource = Backbone.Model.extend({});

    var RammetidResources = Backbone.Collection.extend({
        model: RammetidResource,
        initialize: function (models, options) {
            options || (options = {});
            this.umbrellaOrganisationUri = options.umbrellaOrganisationUri;
        },
        url: function () {
            var url = "/api/booking/v1/resources/";
            url += "?booking_type=rammetid_allowed";
            if (this.umbrellaOrganisationUri) {
                url += "&umbrella_organisation_uri=" + this.umbrellaOrganisationUri;
            }
            return url;
        }
    });

    var Resource = Backbone.Model.extend({});

    ns.Resources = Backbone.Collection.extend({
        model: Resource
    });

    ns.RammetidToApplication = Backbone.Model.extend({
        url: function () {
            var base = "/api/booking/v1/rammetidtoapplication/";
            if (!this.isNew()) {
                base += this.get("id");
            }
            return base;
        }
    });

    ns.RammetidView = Backbone.View.extend({
        template: $("#rammetid_main_template").html(),
        events: {
            "click #save": "save",
            "click #delete": "delete"
        },
        initialize: function (options) {
            _.bindAll(this, "save", "saveSuccess", "saveError", "updateResourcesDropdown", 'showCalendar');

            this.memberOrganisations = options.memberOrganisations;
            this.memberOrganisations.each(function (org, i) {
                // Wrap around colors
                org.set('color', colors[i % colors.length]);
            });

            // Must select resource and period before showing the calendar.
            this.resource = null;
            this.period = null;

            this.calendar = new ns.RammetidCalendar({
                umbrellaOrganisation: options.umbrellaOrganisation,
                memberOrganisations: options.memberOrganisations
            });

            this.availableResources = new ns.Resources(options.resources.models);
            this.resourceSelectView = new DropdownView({
                collection: this.availableResources,
                title: "Lokale"
            });

            // Filter resource drop down to show only
            // the resources that has an rammetid applied
            this.rammetidResources = new RammetidResources([], {
                umbrellaOrganisationUri: options.umbrellaOrganisation.get("uri")
            });

            this.rammetidResources.fetch({
                'success': this.updateResourcesDropdown
            });

            this.memberOrganisationSelectView = new DropdownView({
                collection: this.memberOrganisations,
                title: "Medlemsorganisasjon"
            });

            this.periods = new Periods([], {
                umbrellaOrganisationUri: options.umbrellaOrganisation.get("uri")
            });
            this.periodSelectView = new DropdownView({
                collection: this.periods,
                title: "Periode"
            });

            this.resourceSelectView.on('modelSelected', this.resourceSelected, this);
            this.periodSelectView.on('modelSelected', this.periodSelected, this);
            this.memberOrganisationSelectView.on('modelSelected', this.memberOrganisationSelected, this);

            this.legendView = new LegendView({
                collection: this.memberOrganisations
            });

            this.calendar.on("slotAdded", this.checkSave, this);
            this.calendar.on('slotRemoved', this.checkSave, this);
            this.calendar.on('toggleSlotSelect', this.toggleSlotSelect, this);
        },

        render: function () {
            this.$el.html(_.template(this.template));
            this.periodSelectView.setElement(this.$("#dates_selection"));
            this.periodSelectView.render();
            this.resourceSelectView.setElement(this.$("#resources"));
            this.resourceSelectView.render();
            this.memberOrganisationSelectView.setElement(this.$("#member-organisations"));
            this.memberOrganisationSelectView.render();
            this.$('.legend').html(this.legendView.render().$el.addClass("hidden"));
            this.calendar.setElement(this.$("#calendar"));
        },

        updateResourcesDropdown: function () {
            var rammetidResourcesUris = this.rammetidResources.pluck('uri');
            var resources = this.options.resources.filter(function (model) {
                return _.contains(rammetidResourcesUris, model.get("uri"));
            });
            this.availableResources.reset(resources);
        },

        resourceSelected: function (resource) {
            this.resource = resource;
            if (resource) {
                this.periods.setResource(resource);
                this.periods.fetch({
                    'reset': true,
                    'success': this.showCalendar
                });
            } else {
                this.periods.reset();
                this.showCalendar();
            }
        },

        memberOrganisationSelected: function (memberOrganisation) {
            this.memberOrganisation = memberOrganisation;
            if (!this.calendar.shown) {
                this.showCalendar();
            } else {
                this.calendar.data.memberOrganisation = memberOrganisation;
            }
        },

        periodSelected: function (period) {
            this.period = period;
            this.showCalendar();
        },

        showCalendar: function () {
            if (this.period && this.resource) {
                var start_date = moment();
                start_date.set('month', 8);
                start_date.set('date', 1);
                var end_date = moment();
                end_date.add('year', 1);
                end_date.set('month', 5);
                end_date.set('date', 20);
                this.calendar.show({
                    resource: this.resource,
                    memberOrganisation: this.memberOrganisation,
                    dates: this.period.getDates()
                });
                this.$('.legend').removeClass("hidden");
            } else {
                this.$('.legend').addClass("hidden");
                this.$('#save').prop('disabled', true);
                this.calendar.hide();
            }
        },

        checkSave: function () {
            if (this.calendar.getData().length) {
                this.$('#save').prop('disabled', false);
            } else {
                this.$('#save').prop('disabled', true);
            }
        },

        save: function () {

            if (this.period && this.resource && this.memberOrganisation) {
                var dates = this.period.getDates();


                var organisations = _.reduce(this.calendar.getData(), function (organisations, slot) {
                    var org_uri = this.memberOrganisations.get(slot.get('org_id')).get('organisation').uri;
                    if (!organisations[org_uri]) {
                        organisations[org_uri] = {
                            slots: [],
                            uri: org_uri
                        };
                    }
                    organisations[org_uri].slots.push({
                        start_time: slot.get("start_time").format("HH:mm"),
                        end_time: slot.get("end_time").format("HH:mm"),
                        week_day: slot.get("start_time").isoWeekday(),
                        start_date: moment(dates.start_date).format("YYYY-MM-DD"),
                        end_date: moment(dates.end_date).format("YYYY-MM-DD")
                    });
                    return organisations;
                }, {}, this);

                var data = {
                    organisations: organisations,
                    resource: {
                        uri: this.resource.get("uri")
                    },
                    umbrella_organisation: {
                        uri: this.calendar.umbrellaOrganisation.get('uri')
                    }
                };
                var rammetidToApplication = new ns.RammetidToApplication(data);
                rammetidToApplication.save({}, {
                    success: this.saveSuccess,
                    error: this.saveError
                });
            }
        },

        saveSuccess: function (model, response) {
            this.calendar.resetRows();
            this.$('#save').prop('disabled', true);
        },

        saveError: function (model, xhr, options) {
            var error = JSON.parse(xhr.responseText);
            var errorString = error["__error__"].join(", ");
            this.$el.find("#error_messages").append(
                new ns.Notifier().render(
                    "En feil oppstod under tildeling av rammetid:",
                    error.message || errorString,
                    "error"
                ).$el
            );
        },
        toggleSlotSelect: function (selectedSlots) {
            var canDelete = selectedSlots.length;
            this.$('#delete').prop('disabled', !canDelete);

            this.selectedSlots = selectedSlots;
        },
        'delete': function (event) {
            event.preventDefault();
            if (this.selectedSlots.length) {
                _.each(this.selectedSlots, function (slot) {
                    slot.collection.removeSlot(slot);
                }, this);
            }
            this.toggleSlotSelect([]);
        }
    });

}(Flod));