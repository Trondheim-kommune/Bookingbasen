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
        }
    });

    var ReleaseDateRangeTimePeriodView = Backbone.View.extend({
        template: $("#release_date_range_time_period_repeating_slot_template").html(),
        events: {
            "click #release-date-range-time-period": "releaseDateRangeTimePeriod"
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

            this.timePicker = new ns.TimePicker().render(moment(this.model.get("start_time")), moment(this.model.get("end_time")));
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
        setTimePeriod: function () {
            this.model.set({
                "release_from_time": this.timePicker.start_time.format("HH:mm:ss"),
                "release_to_time": this.timePicker.end_time.format("HH:mm:ss")
            });
        },
        render: function () {
            if (this.model) {
                var data = {
                    "start_date": moment(this.model.get("start_date")).format("DD.MM.YYYY"),
                    "end_date": moment(this.model.get("end_date")).format("DD.MM.YYYY"),
                    "start_time": this.model.get("start_time").format("HH:mm"),
                    "end_time": this.model.get("end_time").format("HH:mm")
                };
                this.$el.html(_.template(this.template, data));
                this.$el.find("#time-picker").append(this.timePicker.$el);
                this.$el.find("#date-selection").append(this.dateRangeSelectView.render().$el);
            }
            return this;
        },
        releaseDateRangeTimePeriod: function () {
            this.setTimePeriod();
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
            var from_date = this.model.get("release_from_date");
            var to_date = this.model.get("release_to_date");
            var from_time = this.model.get("release_from_time");
            var to_time = this.model.get("release_to_time");
            this.$el.append(
                new ns.Notifier().render(
                    "Tid frigitt!",
                    "Følgende periode/tidspunkt ble frigitt: " +
                    moment(from_date).format("DD.MM.YYYY") + " - " + moment(to_date).format("DD.MM.YYYY") +
                    " (" + moment(from_time, "HH:mm:ss").format("HH:mm") + " - " + moment(to_time, "HH:mm:ss").format("HH:mm") + ")",
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
            'click #release-date-range-time-period': 'releaseDateRangeTimePeriod'
        },
        initialize: function () {
            _.bindAll(this, "releaseDateRangeTimePeriod");
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
        releaseDateRangeTimePeriod: function () {
            var model = new ReleaseTimeRepeatingSlot({
                id: this.model.get("id"),
                start_date: this.model.get("start_date"),
                end_date: this.model.get("end_date"),
                start_time: moment(this.model.get("start_time"), "HH.mm.ss"),
                end_time: moment(this.model.get("end_time"), "HH.mm.ss")
            });
            this.trigger("release-date-range-time-period", model);
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
            view.on("release-date-range-time-period", function (model, error) {
                this.trigger("release-date-range-time-period", model);
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

            var releaseDateRangeTimePeriodView = new ReleaseDateRangeTimePeriodView({
                repeatingApplication: this.model
            });
            this.repatingApplicationView.on("release-date-range-time-period", function (releaseTimeRepeatingSlot) {
                releaseDateRangeTimePeriodView.setModel(releaseTimeRepeatingSlot);
                $("#repeating-date-range-time-period-changer").show();
            });
            $("#repeating-date-range-time-period-changer").append(releaseDateRangeTimePeriodView.render().$el);
        },
        render: function () {
            this.$el.find("#repeating-application").append(this.repatingApplicationView.render().$el);
        }
    });

}(Flod));
