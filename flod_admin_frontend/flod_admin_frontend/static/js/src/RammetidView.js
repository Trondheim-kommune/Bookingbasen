var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var colors = [
        '#C00000', '#996633', '#00C000', '#C0FFC0', '#0000C0',
        '#404000', '#C0C000', '#008080', '#00FFFF', '#C000C0',
        '#C05800', '#663399', '#990033', '#FF0099', '#FFC0C0'
    ];

    function localStorageAvailable() {
        return ('localStorage' in window && window['localStorage'] !== null);
    }

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
            this.selectedId = options.selectedId;
            _.bindAll(this, "change");
        },
        render: function () {
            var data = {
                title: this.title,
                values: this.collection.map(function (model) {
                    return {
                        id: model.get("id"),
                        name: model.get("name")
                    };
                })
            };
            this.$el.html(_.template(this.template, data));
            this.$el.find('option[value="' + this.selectedId + '"]').prop('selected', true);
            return this;
        },
        change: function () {
            var model_id = this.$("select").val();
            var model = this.collection.get(model_id);
            this.trigger("modelSelected", model);
        }
    });

    var PeriodView = Backbone.View.extend({
        template: $("#dates_select_template").html(),
        initialize: function () {
            _.bindAll(this, 'dateChanged');
        },

        render: function () {
            console.log(this.model);
            this.$el.html(_.template(this.template));

            this.$("#start_date_div").datepicker({
                "format": 'dd.mm.yyyy',
                "weekStart": 1,
                "autoclose": true
            })
                .on('changeDate', this.dateChanged);
            if (this.model.get('start_date') && this.model.get('start_date').isValid()) {
                this.$("#start_date_div").datepicker('setDate', this.model.get('start_date').toDate());
            }

            this.$("#end_date_div").datepicker({
                "format": 'dd.mm.yyyy',
                "weekStart": 1,
                "autoclose": true
            })
                .on('changeDate', this.dateChanged);
            if (this.model.get('end_date') && this.model.get('end_date').isValid()) {
                this.$("#end_date_div").datepicker('setDate', this.model.get('end_date').toDate());
            }
            return this;
        },

        getPeriod: function () {
            return new Period({
                "start_date": moment(this.$("#start_date").val(), "DD.MM.YYYY"),
                "end_date": moment(this.$("#end_date").val(), "DD.MM.YYYY")
            });
        },

        dateChanged: function () {
            var period = this.getPeriod();
            if (period.get('start_date') && period.get('end_date')) {
                this.trigger("dateChange", period);
            }
        }
    });
    var Period = Backbone.Model.extend({
        getDates: function () {
            return {
                "start_date": this.get("start_date"),
                "end_date": this.get("end_date")
            };
        }
    });

    var UmbrellaOrganisation = Backbone.Model.extend({
    });

    ns.UmbrellaOrganisations = Backbone.Collection.extend({
        model: UmbrellaOrganisation,
        getByUri: function (uri) {
            return this.where({uri: uri})[0];
        }
    });

    ns.Resources = Backbone.Collection.extend({
        comparator : function(resource) {
            return resource.get('name').toUpperCase();
        }
    });

    ns.RammetidView = Backbone.View.extend({
        template: $("#rammetid_main_template").html(),
        events: {
            "click #save": "save"
        },
        initialize: function (options) {
            _.bindAll(this, "save", "saveSuccess", "saveError", "saveDropDownsToLocalStorage");

            // Must select resource, period and umbrella
            // organisation before showing the calendar,
            // or models are pre-selected from local storage.
            this.resource = null;
            this.period = null;
            this.umbrellaOrganisation = null;

            options.umbrellaOrganisations.each(function (org, i) {
                // Wrap around colors
                org.set('color', colors[i % colors.length]);
            });

            this.calendar = new ns.RammetidCalendar({
                umbrellaOrganisations: options.umbrellaOrganisations
            });

            var localStorageSupported = localStorageAvailable();

            var selectedResourceId = 0;
            if (localStorageSupported) {
                var resourceId = localStorage.getItem("rammetid_resource_id");
                this.resource = options.resources.get(resourceId);
                if (this.resource) {
                    selectedResourceId = this.resource.get("id");
                }
            }
            this.resourceSelectView = new DropdownView({
                collection: options.resources,
                title: "Lokale",
                selectedId: selectedResourceId
            });

            var selectedUmbrellaOrganisationId = 0;
            if (localStorageSupported) {
                var umbrellaOrganisationId = localStorage.getItem('rammetid_umbrella_organisation_id');
                this.umbrellaOrganisation = options.umbrellaOrganisations.get(umbrellaOrganisationId);
                if (this.umbrellaOrganisation) {
                    selectedUmbrellaOrganisationId = this.umbrellaOrganisation.get("id");
                }
            }
            this.umbrellaOrganisationsSelectView = new DropdownView({
                collection: options.umbrellaOrganisations,
                title: "Paraplyorganisasjon",
                selectedId: selectedUmbrellaOrganisationId
            });

            if (localStorageSupported) {
                var data = {
                    start_date: moment(localStorage.getItem('rammetid_period_start_date'), 'YYYY-MM-DD'),
                    end_date: moment(localStorage.getItem('rammetid_period_end_date'), 'YYYY-MM-DD')
                };
                this.period = new Period(data);
            }
            this.periodSelectView = new PeriodView({'model': this.period});

            this.resourceSelectView.on('modelSelected', this.resourceSelected, this);
            this.umbrellaOrganisationsSelectView.on('modelSelected', this.umbrellaOrganisationSelected, this);
            this.periodSelectView.on('dateChange', this.periodSelected, this);

            this.legendView = new LegendView({
                collection: options.umbrellaOrganisations
            });

            this.calendar.on("slotAdded", this.checkSave, this);
        },
        render: function () {
            this.$el.html(_.template(this.template));
            this.periodSelectView.setElement(this.$("#dates_selection"));
            this.periodSelectView.render();
            this.umbrellaOrganisationsSelectView.setElement(this.$("#organisations"));
            this.umbrellaOrganisationsSelectView.render();
            this.resourceSelectView.setElement(this.$("#resources"));
            this.resourceSelectView.render();
            this.$('.legend').html(this.legendView.render().$el.addClass("hidden"));
            this.calendar.setElement(this.$("#calendar"));
            this.showCalendar();
        },
        resourceSelected: function (resource) {
            this.resource = resource;
            this.saveDropDownsToLocalStorage();
            this.showCalendar();
        },
        umbrellaOrganisationSelected: function (umbrellaOrganisation) {
            this.umbrellaOrganisation = umbrellaOrganisation;
            this.saveDropDownsToLocalStorage();
            if (!this.calendar.shown) {
                this.showCalendar();
            } //do not re-load calendar if already shown!
        },
        periodSelected: function (period) {
            this.period = period;
            this.saveDropDownsToLocalStorage();
            this.showCalendar();
        },
        showCalendar: function () {
            if (this.period && this.resource && this.umbrellaOrganisation) {
                this.calendar.show({
                    resource: this.resource,
                    umbrellaOrganisation: this.umbrellaOrganisation,
                    dates: this.period.getDates()
                });
                this.$('.legend').removeClass("hidden");
            } else {
                this.$('.legend').addClass("hidden");
                this.$("#save").addClass("hidden");
                this.calendar.hide();
            }
        },
        checkSave: function () {
            if (this.calendar.getData().length) {
                this.$("#save").removeClass("hidden");
            }
        },
        save: function () {
            if (this.period && this.resource && this.umbrellaOrganisation) {
                var dates = this.period.getDates();
                var rammetidSlots = _.map(this.calendar.getData(), function (slot) {
                    return {
                        start_time: slot.get("start_time").format("HH:mm"),
                        end_time: slot.get("end_time").format("HH:mm"),
                        week_day: slot.get("start_time").isoWeekday(),
                        start_date: moment(dates.start_date).format("YYYY-MM-DD"),
                        end_date: moment(dates.end_date).format("YYYY-MM-DD")
                    };
                }, this);
                var data = {
                    rammetid_slots: rammetidSlots,
                    resource: {
                        uri: this.resource.get("uri")
                    },
                    umbrella_organisation: {
                        uri: this.umbrellaOrganisation.get("uri")
                    }
                };
                var rammetid = new ns.Rammetid(data);
                rammetid.save({}, {
                    success: this.saveSuccess,
                    error: this.saveError
                });
            }
        },
        saveSuccess: function (model, response) {
            this.calendar.resetRows();
            this.$("#save").addClass("hidden");
        },
        saveError: function (model, response) {
            var error = JSON.parse(response.responseText);
            var errorString = error["__error__"].join(", ");

            this.$("#error-messages").prepend(
                new ns.Notifier().render(
                    "En feil oppstod!",
                    error.message || errorString,
                    "error"
                ).$el
            );
        },
        saveDropDownsToLocalStorage: function () {
            if (localStorageAvailable()) {
                if (this.umbrellaOrganisation) {
                    localStorage.setItem('rammetid_umbrella_organisation_id', this.umbrellaOrganisation.get("id"));
                }
                if (this.period) {
                    localStorage.setItem('rammetid_period_start_date', this.period.get("start_date").format('YYYY-MM-DD'));
                    localStorage.setItem('rammetid_period_end_date', this.period.get("end_date").format('YYYY-MM-DD'));
                }
                if (this.resource) {
                    localStorage.setItem('rammetid_resource_id', this.resource.get("id"));
                }
            }
        }
    });

}(Flod));