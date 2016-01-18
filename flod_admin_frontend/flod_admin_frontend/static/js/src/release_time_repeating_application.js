var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var DateRangeSelectView = Backbone.View.extend({
        template: $("#dates_select_template").html(),
        className: "row-fluid",
        initialize: function () {
            _.bindAll(this, 'dateChanged');
        },
        render: function () {
            this.$el.html(_.template(this.template));
            this.$("#start_date_div").datepicker({
                "format": 'dd.mm.yyyy',
                "weekStart": 1,
                "autoclose": true
            })
                .on('changeDate', this.dateChanged)
                .datepicker('setDate', this.options.start_date.toDate());

            this.$("#end_date_div").datepicker({
                "format": 'dd.mm.yyyy',
                "weekStart": 1,
                "autoclose": true
            })
                .on('changeDate', this.dateChanged)
                .datepicker('setDate', this.options.end_date.toDate());
            return this;
        },
        getDates: function () {
            return {
                "start_date": moment(this.$el.find("#start_date").val(), "DD.MM.YYYY"),
                "end_date": moment(this.$el.find("#end_date").val(), "DD.MM.YYYY")
            };
        },
        dateChanged: function () {
            this.trigger("dateChange", this.getDates());
        }
    });

    var ReleaseTimeRepeatingSlot = Backbone.Model.extend({
        url: function () {
            return "/api/booking/v1/repeating_slots/" + this.get("id") + "/release_time";
        },
        validate: function (attrs, options) {
            if (_.has(attrs, "release_from_date") || _.has(attrs, "release_to_date")) {
                var release_from_date = moment(attrs['release_from_date']);
                var release_to_date = moment(attrs['release_to_date']);
                var start_date = moment(attrs['start_date']);
                var end_date = moment(attrs['end_date']);
                if (release_from_date.isAfter(release_to_date)) {
                    return "Startdato er etter sluttdato.";
                }
                if ((release_from_date.isBefore(start_date) || release_from_date.isSame(start_date)) &&
                    (release_to_date.isAfter(end_date) || release_to_date.isSame(end_date))) {
                    return "Du kan ikke frigi hele perioden.";
                }
            }
            if (_.has(attrs, "release_from_time") || _.has(attrs, "release_to_time")) {
                var release_from_time = moment(attrs['release_from_time'], "HH.mm.ss");
                var release_to_time = moment(attrs['release_to_time'], "HH.mm.ss");
                var start_time = moment(attrs['start_time'], "HH.mm.ss");
                var end_time = moment(attrs['end_time'], "HH.mm.ss");
                if (release_from_time.unix() > release_to_time.unix()) {
                    return "Starttidspunkt er etter slutttidspunkt.";
                }
                if (release_from_time <= start_time && release_to_time >= end_time) {
                    return "Du kan ikke frigi hele tidsperioden.";
                }
            }
        }
    });

    var ReleaseDateRangeView = Backbone.View.extend({
        template: $("#release_date_range_repeating_slot_template").html(),
        events: {
            "click #release-date-range": "releaseDateRange"
        },
        initialize: function () {
            _.bindAll(this, "setReleaseDateRange", "saveSuccess", "saveError",
                "errorMessage", "successMessage");
        },
        setModel: function (model) {
            this.model = model;
            this.dateRangeSelectView = new DateRangeSelectView({
                "start_date": moment(this.model.get("start_date")),
                "end_date": moment(this.model.get("end_date"))
            });
            this.model.set({
                "release_from_date": moment(this.model.get("start_date")).format("YYYY-MM-DD"),
                "release_to_date": moment(this.model.get("end_date")).format("YYYY-MM-DD")
            });
            this.dateRangeSelectView.on('dateChange', this.setReleaseDateRange);
            this.model.on("invalid", function (model, errorMessage) {
                this.errorMessage(errorMessage);
            }, this);
            this.render();
        },
        setReleaseDateRange: function (dates) {
            this.model.set({
                "release_from_date": dates.start_date ? moment(dates.start_date).format("YYYY-MM-DD") : null,
                "release_to_date": dates.end_date ? moment(dates.end_date).format("YYYY-MM-DD") : null
            });
        },
        render: function () {
            if (this.model) {
                var data = {
                    "start_date": moment(this.model.get("start_date")).format("DD.MM.YYYY"),
                    "end_date": moment(this.model.get("end_date")).format("DD.MM.YYYY")
                };
                this.$el.html(_.template(this.template, data));
                this.$el.find("#date-selection").append(this.dateRangeSelectView.render().$el);
            }
            return this;
        },
        releaseDateRange: function () {
            if (this.model.isValid()) {
                this.model.save(
                    {},
                    {
                        success: this.saveSuccess,
                        error: this.saveError
                    }
                );
            }
        },
        saveSuccess: function (model, response, options) {
            this.options.repeatingApplication.get("slots").remove(model.get("id"));
            // One or more slots generated after released time
            for (var i = 0; i < response.length; i++) {
                if (model.has(i)) {
                    this.options.repeatingApplication.get("slots").add(model.get(i));
                }
            }
            this.$el.empty();
            this.successMessage();
        },
        saveError: function (model, xhr, options) {
            var error = JSON.parse(xhr.responseText);
            if (error["__error__"]) {
                var errorString = error["__error__"].join(", ");
            }
            this.errorMessage(errorString || error.message);
        },
        successMessage: function () {
            var from = this.model.get("release_from_date");
            var to = this.model.get("release_to_date");
            this.$el.append(
                new ns.Notifier().render(
                    "Tid frigitt!",
                    "Følgende dato(er) ble frigitt: " + from + " - " + to,
                    "success"
                ).$el
            );
        },
        errorMessage: function (message) {
            this.$el.append(
                new ns.Notifier().render(
                    "En feil oppstod:",
                    message,
                    "error"
                ).$el
            );
        }
    });

    var ReleaseTimePeriodView = Backbone.View.extend({
        template: $("#release_time_period_repeating_slot_template").html(),
        events: {
            "click #release-time-period": "releaseTimePeriod"
        },
        initialize: function () {
            _.bindAll(this, "setTimePeriod", "saveSuccess", "saveError",
                "errorMessage", "successMessage");
        },
        setModel: function (model) {
            this.model = model;
            this.timePicker = new ns.TimePicker().render(moment(this.model.get("start_time")), moment(this.model.get("end_time")));
            this.model.on("invalid", function (model, errorMessage) {
                this.errorMessage(errorMessage);
            }, this);
            this.render();
        },
        setTimePeriod: function () {
            this.model.set({
                "release_from_time": this.timePicker.start_time.format("HH:mm:ss"),
                "release_to_time": this.timePicker.end_time.format("HH:mm:ss")
            });
        },
        render: function () {
            if (this.model) {
                var data = {
                    "start_time": this.model.get("start_time").format("HH:mm"),
                    "end_time": this.model.get("end_time").format("HH:mm")
                };
                this.$el.html(_.template(this.template, data));
                this.$el.find("#time-picker").append(this.timePicker.$el);
            }
            return this;
        },
        releaseTimePeriod: function () {
            this.setTimePeriod();
            if (this.model.isValid()) {
                this.model.save({},
                    {
                        success: this.saveSuccess,
                        error: this.saveError
                    });
            }
        },
        saveSuccess: function (model, response, options) {
            this.options.repeatingApplication.get("slots").remove(model.get("id"));
            // One or more slots generated after released time
            for (var i = 0; i < response.length; i++) {
                if (model.has(i)) {
                    this.options.repeatingApplication.get("slots").add(model.get(i));
                }
            }
            this.$el.empty();
            this.successMessage();
        },
        saveError: function (model, xhr, options) {
            var error = JSON.parse(xhr.responseText);
            if (error["__error__"]) {
                var errorString = error["__error__"].join(", ");
            }
            this.errorMessage(errorString || error.message);
        },
        successMessage: function () {
            var from = this.model.get("release_from_time");
            var to = this.model.get("release_to_time");
            this.$el.append(
                new ns.Notifier().render(
                    "Tid frigitt!",
                    "Følgende tidspunkt ble frigitt: " + from + " - " + to,
                    "success"
                ).$el
            );
        },
        errorMessage: function (message) {
            this.$el.append(
                new ns.Notifier().render(
                    "En feil oppstod:",
                    message,
                    "error"
                ).$el
            );
        }
    });

    var RepeatingSlot = Backbone.Model.extend({});

    var RepeatingSlots = Backbone.Collection.extend({
        model: RepeatingSlot,
        comparator: function (model) {
            return -moment(model.get("start_date")).valueOf();
        }
    });

    ns.RepeatingApplication = Backbone.Model.extend({
        url: function () {
            return "/api/booking/v1/applications/" + this.get("id");
        },
        parse: function (response) {
            response["slots"] = new RepeatingSlots(response["slots"]);
            return response;
        }
    });

    var RepeatingSlotView = Backbone.View.extend({
        template: $("#repeating_slot_template").html(),
        events: {
            'click #release-date-range': 'releaseDateRange',
            'click #release-time-period': 'releaseTimePeriod'
        },
        initialize: function () {
            _.bindAll(this, "releaseDateRange", "releaseTimePeriod");
        },
        render: function () {
            var data = {
                day: ns.capitaliseFirstLetter(ns.getTextualWeekDay(this.model.get("week_day"))) + "er",
                start_time: moment(this.model.get("start_time"), "HH.mm.ss").format("HH:mm"),
                end_time: moment(this.model.get("end_time"), "HH.mm.ss").format("HH:mm"),
                start_date: moment(this.model.get("start_date"), "YYYY-MM-DD").format("DD.MM.YYYY"),
                end_date: moment(this.model.get("end_date"), "YYYY-MM-DD").format("DD.MM.YYYY")
            };
            this.$el.html(_.template(this.template, data));
            return this;
        },
        releaseDateRange: function () {
            var model = new ReleaseTimeRepeatingSlot({
                id: this.model.get("id"),
                start_date: this.model.get("start_date"),
                end_date: this.model.get("end_date")
            });
            this.trigger("release-date-range", model);
        },
        releaseTimePeriod: function () {
            var model = new ReleaseTimeRepeatingSlot({
                id: this.model.get("id"),
                start_time: moment(this.model.get("start_time"), "HH.mm.ss"),
                end_time: moment(this.model.get("end_time"), "HH.mm.ss")
            });
            this.trigger("release-time-period", model);
        }
    });

    var RepeatingApplicationView = Backbone.View.extend({
        template: $("#application_template").html(),
        initialize: function () {
            this.model.get("slots").on("add", function () {
                this.renderRepeatingSlots();
            }, this);
        },
        render: function () {
            var data = {
                "aktor": this.model.get("organisation").name,
                "resource": this.model.get("resource").name
            };
            this.$el.html(_.template(this.template, data));
            this.renderRepeatingSlots();
            return this;
        },
        renderRepeatingSlots: function () {
            this.$el.find('#repeating-slots').empty();
            _.each(this.model.get("slots").models, function (model) {
                this.renderRepeatingSlot(model);
            }, this);
        },
        renderRepeatingSlot: function (model) {
            var view = new RepeatingSlotView({
                model: model
            });
            // Just forward the events
            view.on("release-date-range", function (model, error) {
                this.trigger("release-date-range", model);
            }, this);
            view.on("release-time-period", function (model, error) {
                this.trigger("release-time-period", model);
            }, this);
            this.$el.find('#repeating-slots').append(view.render().$el);
        }
    });

    ns.ReleaseTimeRepeatingApplicationView = Backbone.View.extend({
        template: $("#release_time_repeating_application").html(),
        initialize: function () {
            this.repatingApplicationView = new RepeatingApplicationView({
                model: this.model
            });

            var releaseTimePeriodView = new ReleaseTimePeriodView({
                repeatingApplication: this.model
            });
            this.repatingApplicationView.on("release-time-period", function (releaseTimeRepeatingSlot) {
                releaseTimePeriodView.setModel(releaseTimeRepeatingSlot);
                $("#repeating-date-range-changer").hide();
                $("#repeating-time-period-changer").show();
            });
            $("#repeating-time-period-changer").append(releaseTimePeriodView.render().$el);

            var releaseDateRangeView = new ReleaseDateRangeView({
                repeatingApplication: this.model
            });
            this.repatingApplicationView.on("release-date-range", function (releaseTimeRepeatingSlot) {
                releaseDateRangeView.setModel(releaseTimeRepeatingSlot);
                $("#repeating-date-range-changer").show();
                $("#repeating-time-period-changer").hide();
            });
            $("#repeating-date-range-changer").append(releaseDateRangeView.render().$el);
        },
        render: function () {
            this.$el.find("#repeating-application").append(this.repatingApplicationView.render().$el);
        }
    });

}(Flod));
