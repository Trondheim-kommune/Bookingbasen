var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var BookingForm = Backbone.View.extend({

        template: $("#strotime_booking_template").html(),

        render: function () {

            this.start_time = this.options.start_time;
            this.last_end = this.options.last_end;

            this.timePicker = new ns.TimePicker().render(
                this.start_time,
                this.last_end
            );

            this.$el.html(_.template(
                this.template,
                {
                    "model": this.options.facility.toJSON(),
                    "time": this.start_time,
                    endTime: this.last_end
                }
            ));
            this.$el.append(this.timePicker.$el);
            return this;
        },

        getData: function () {
            return {
                "start_time": this.timePicker.start_time,
                "end_time": this.timePicker.end_time,
                "resource": {"uri": this.options.facility.get("uri")}
            };
        },

        showError: function (error) {
            this.$el.append(error);
        }
    });

    function getThreeWeekPeriod(start) {
        var first_day = moment(start);
        return {
            "start": moment(first_day).add("days", 3),
            "end": moment(first_day).add("days", 21)
        };
    }

    var StrotimeApplication = Flod.SingleApplication.extend({

        "url": "/api/booking/v1/applications/strotime/",

        toJSON: function () {
            return Backbone.Model.prototype.toJSON.apply(this, arguments);
        }
    });

    var Resource = Backbone.Model.extend({

        initialize: function () {
            this.set({
                "slots": new ns.Slots([], {
                    resource_uri: this.get("uri")
                }),
                "blocks": new ns.BlockedSlots([], {
                    resource_uri: this.get("uri"),
                    type: 'blockedtimes'
                }),
                "rammetid_slots": new ns.RammetidSlots([], {
                    split_by_slots: true,
                    resource_uri: this.get("uri")
                })
            });
        },

        fetchSlotsAndBlocks: function (date, callback) {
            var fetcted = _.after(3, callback);
            this.fetchSlots(date, fetcted);
            this.fetchReservedTimes(date, fetcted);
            this.fetchRammetidSlots(date, fetcted);
        },

        fetchSlots: function (date, callback) {
            var slot = this.get("slots");
            slot.options['day'] = date.format("YYYY-MM-DD");
            slot.options['status'] = 'Granted';
            slot.fetch({"success": callback});
        },

        fetchReservedTimes: function (date, callback) {
            var block = this.get("blocks");
            block.options['date'] = date.format("YYYY-MM-DD");
            block.fetch({"success": callback});
        },

        fetchRammetidSlots: function(date, callback) {
            var rammetid_slots = this.get("rammetid_slots");
            rammetid_slots.options['start_date'] = date.format("YYYY-MM-DD");
            rammetid_slots.options['end_date'] = date.format("YYYY-MM-DD");
            rammetid_slots.options['split_by_arrangement_slots'] = true;
            rammetid_slots.options['split_by_slots'] = true;
            rammetid_slots.fetch({"success": callback});
        }
    });

    var Resources = Backbone.Collection.extend({

        model: Resource,

        url: "/api/booking/v1/resources"

    });

    ns.StrotimeCalendar = Backbone.View.extend({

        initialize: function () {
            this.resources = new Resources();
            _.bindAll(this, "slotsFetched", "fetchSlots");

            this.calendar = new ns.CalendarView();
            this.date = this.options.startDate || moment();
            var range = getThreeWeekPeriod(this.date);
            var week = new Flod.Week({
                "year": this.date.year(),
                "week": this.date.isoWeek(),
                "range": range
            });

            this.weekView = new Flod.WeekView({
                "model": week,
                "selected": moment(range.start)
            });
            this.weekView.on("changeDay", this.fetchSlots);
            this.weekView.change(moment(range.start));
        },

        setResources: function (facilities) {
            if (facilities) {
                this.resources.reset(facilities.map(function (facility) {
                    return {
                        "uri": facility.get("uri"),
                        "name": facility.get("name")
                    };
                }));
                this.fetchSlots(this.date);
                this.$el.show();
            } else {
                this.resources.reset();
                this.$el.hide();
            }
        },

        render: function () {
            this.$el.html("");
            this.calendar.model.set({"title": this.date.format("dddd")});
            this.calendar.model.set({"subtitle": this.date.format("D.M")});

            this.$el.append(this.weekView.render().$el);
            this.$el.append(this.calendar.render().$el);
            if (!this.resources.length) {
                this.$el.hide();
            }
            this.$el.append($("#calendar_legend_template").html());
            return this;
        },

        fetchSlots: function (date) {
            this.date = date;
            this.render();

            var finished = _.after(this.resources.length, this.slotsFetched);
            this.resources.each(function (resource) {
                resource.fetchSlotsAndBlocks(date, finished);
            });
        },

        slotsFetched: function () {
            var rows = this.resources.map(function (resource) {
                var blocks = resource.get("blocks").models;

                var slots = ns.findCollisionsSlots(resource.get("slots").models);

                // Remove those rammetid slots that are not on the selected week day.
                var rammetid_slots = resource.get("rammetid_slots").filter(function (model) {
                    return _.isEqual(model.get("week_day"), this.date.isoWeekday());
                }, this);

                _.each(rammetid_slots, function (rammetid_slot) {
                    //adjust date to today so that collision detection works
                    rammetid_slot.changeDate(this.date);
                }, this);

                var concatinated = slots.concat(blocks).concat(rammetid_slots);
                var allSlots = ns.findCollisionsSlots(concatinated);

                //change styling on collision slots
                _.each(allSlots, function (slot) {
                    if (slot instanceof ns.CollisionSlot) {
                        slot.set({
                            status: 'reserved',
                            display_name: 'Enheten har reservert lokalet til eget bruk'
                        });
                    }
                });
                return new ns.CalendarRow(
                    allSlots,
                    {
                        "date": this.date,
                        "displayName": resource.get("name"),
                        "resource_uri": resource.get("uri")
                    }
                );
            }, this);

            this.calendar.model.reset(rows);
        }
    });

    var Facilities = Backbone.Collection.extend({

        url: "/facilities/strotime/"

    });

    ns.StrotimeBookingView = Backbone.View.extend({

        initialize: function () {
            _.bindAll(this, "bookingSaved", "bookingError");
            this.typeSelector = new Flod.FacilityTypeSelector({
                "collection": this.options.facility_types
            }).render();
            this.facilities = new Facilities();

            this.facilities.on("reset", this.facilitiesFetched, this);
            var startDate = this.options.startDate || moment();
            this.calendar = new ns.StrotimeCalendar({"startDate": startDate});
            this.typeSelector.on("select", this.selectType, this);
            this.calendar.calendar.on("emptySlotClick", this.emptySlotClick, this);
        },

        render: function () {
            this.calendar.setResources(this.facilities);
            this.$el.html(_.template($("#strotime_type_selector_template").html()));
            this.$("form").append(this.typeSelector.$el);
            this.$el.append(this.calendar.render().$el);
            this.$el.append("<div class='alert' style='display: none;'></div>");
            return this;
        },

        facilitiesFetched: function () {
            if (this.facilities.length) {
                this.$(".alert").hide().text("");
                this.calendar.setResources(this.facilities);
            } else {
                this.calendar.setResources();
                this.$(".alert").show().text("Ingen lokaler funnet");
            }
        },

        emptySlotClick: function (data) {

            var facility = this.facilities.find(function (facility) {
                return (facility.get("uri") === data.row.options.resource_uri);
            });

            var start_time = moment(data.row.date)
                .hours(data.start_time.hours())
                .minutes(data.start_time.minutes())
                .seconds(0);

            this.bookingForm = new BookingForm({
                "facility": facility,
                "start_time": start_time,
                "last_end": data.row.getAvailableSpan(start_time)
            });
            this.modal = new Flod.Modal({
                "template_data": {
                    "title": "Book strøtime",
                    "btn_txt": "Book",
                    "btn_cancel_txt": "Avbryt"
                }
            });
            this.modal.render();
            this.modal.$(".modal-body").html(this.bookingForm.render().$el);
            this.modal.on("submit", this.saveBooking, this);
            this.modal.show();
        },

        saveBooking: function () {
            var person = {"uri": window.loggedInUser.get("uri")};
            var data = this.bookingForm.getData();
            data.person = person;
            this.modal.off("submit", this.saveBooking);
            var timeslotData = new Flod.TimeSlot(data).toJSON();
            timeslotData = _.omit(timeslotData, "status", "person", "organisation", "resource");
            var application = new StrotimeApplication({
                "slots": [timeslotData],
                "person": person,
                "text": "",
                "resource": {"uri": data.resource.uri}
            });
            application.save({}, {
                "success": this.bookingSaved,
                "error": this.bookingError
            });
        },

        bookingSaved: function (model) {
            var slot = model.get("slots")[0];
            var row = _.find(this.calendar.calendar.model.get("rows"), function (row) {
                return (row.options.resource_uri === model.get('resource').uri);
            });
            row.addSlot(slot);

            this.modal.hide();
            this.modal = null;
            this.$el.prepend(new ns.Notifier().render(
                "Strøtime reservert",
                "Strøtimen er nå reservert",
                "success"
            ).$el);
        },

        bookingError: function (model, response) {
            this.modal.hide();
            this.modal = null;

            var responseText = $.parseJSON(response.responseText);

            var errorString = responseText["__error__"].join(", ");

            this.$el.prepend(new ns.Notifier().render(
                "En feil oppstod",
                errorString,
                "error"
            ).$el);
        },

        selectType: function (type) {
            if (!type) {
                this.facilities.reset();
            } else {
                this.facilities.fetch({
                    "reset": true,
                    "data": {
                        "facility_type": type
                    }
                });
            }
        }

    });

}(Flod));
