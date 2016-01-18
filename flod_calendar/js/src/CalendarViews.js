var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var BaseView = Backbone.View.extend({

        editable: true,

        initialize: function () {

            this.calendar = new ns.CalendarModel({
                "rows": [],
                "title": "",
                "subtitle": "",
                "editable": this.editable
            });

            this.calendarView = new Flod.CalendarView({"model": this.calendar});
            this.calendarView.on("emptySlotClick", this.emptySlotClick, this);
            this.calendarView.on("slotClick", this.slotClick, this);
        },

        render: function () {
            this.resetRows();
            this.$el.append(this.calendarView.render().$el);
            return this;
        },

        emptySlotClick: function (data) {
            this.trigger("emptySlotClick", data);
        },

        slotClick: function (data) {
            this.trigger("slotClick", data);
        },

        resetRows: function () {
            this.calendarView.model.reset(
                _.map(this.getDays(this.getInitDate()), function (day) {
                    return {"displayName": day.moment.format("dddd"), "date": day.moment};
                })
            );
        },

        getDays: function (date) {
            var week = new Flod.Week({
                "year": date.year(),
                "week": date.isoWeek()
            });

            return week.getDays();
        }
    });

    var Slots = Backbone.Collection.extend({

        model: ns.TimeSlot,
        type: "slots",

        initialize: function (models, options) {
            this.options = options;
        },

        url: function () {
            var url = "/api/booking/v1/resources" + this.options.resource_uri + "/" + this.type + "/";
            if (this.options.start_date && this.options.end_date) {
                url += "?start_date=" + this.options.start_date + "&end_date=" + this.options.end_date;
            }
            return url;
        }
    });

    var mapSlots = function (res, slot) {
        var date = slot.get("start_time").format("YYYY-MM-DD");
        if (!res[date]) {
            res[date] = [];
        }
        res[date].push(slot);
        return res;
    };


    ns.BrowsableWeeklyCalendarView = BaseView.extend({

        getBlocked: true,

        initialize: function () {
            BaseView.prototype.initialize.apply(this, arguments);
            this.currentWeek = new Flod.Week({
                "year": this.getInitDate().isoWeekYear(),
                "week": this.getInitDate().isoWeek()
            });
            this.weeksChooser = new Flod.WeeksView({"model":  new Flod.Weeks({
                "week": this.currentWeek
            })});
            this.weeksChooser.on("changeWeek", this.changeWeek, this);
            this.rows = [];

            _.bindAll(this, "slotsFectched");
        },

        changeWeek: function (week) {
            var currentRows = _.clone(this.calendarView.model.get("rows"));
            var at = _.find(this.rows, function (row) {
                return row.week.equals(this.currentWeek);
            }, this);
            if (at) {
                at.rows = currentRows;
            } else {
                this.rows.push({"week": this.currentWeek, "rows": currentRows});
            }

            this.currentWeek = week;
            var to = _.find(this.rows, function (row) {
                return row.week.equals(week);
            }, this);
            if (to) {
                this.calendarView.model.reset(to.rows);
            } else {
                this.resetRows();
            }
            this.calendarView.render();
        },

        render: function () {
            BaseView.prototype.render.apply(this, arguments);
            this.$el.append(this.weeksChooser.render().$el);
            this.$el.append(this.calendarView.render().$el);
            return this;
        },

        getInitDate: function () {
            return moment(this.options.data.date);
        },

        resetRows: function () {
            var days = this.currentWeek.getDays();
            this.trigger("resetRows", days);

            var slots = new Slots([], {
                "resource_uri": this.options.data.resource.get("uri"),
                "start_date": days[0].moment.format("YYYY-MM-DD"),
                "end_date": days[days.length - 1].moment.format("YYYY-MM-DD")
            });


            if (this.getBlocked) {
                var blocked = new Slots([], {
                    "resource_uri": this.options.data.resource.get("uri"),
                    "start_date": days[0].moment.format("YYYY-MM-DD"),
                    "end_date": days[days.length - 1].moment.format("YYYY-MM-DD")
                });
                blocked.type = "blockedtimes";
                var showSlots = _.after(2, _.bind(function () {
                    this.slotsFectched(slots, blocked);
                }, this));

                slots.fetch({"success": showSlots});
                blocked.fetch({"success": showSlots});
            } else {
                slots.fetch({"success": _.bind(function () {
                    this.slotsFectched(slots);
                }, this)});
            }
        },

        slotsFectched: function (slots, blocked) {
            var mappedSlots = slots.reduce(mapSlots, {});


            if (blocked) {
                blocked.each(function (slot) {
                    slot.set("status", "reserved");
                });

                var mappedBlocked = blocked.reduce(mapSlots, {});

                _.each(mappedBlocked, function (value, key) {
                    if (_.has(mappedSlots, key)) {
                        mappedSlots[key] = mappedSlots[key].concat(value);
                    } else {
                        mappedSlots[key] = value;
                    }
                });
            }

            _.each(mappedSlots, function (slots, date) {
                var row = _.find(this.calendar.get("rows"), function (row) {
                    return row.date.isSame(moment(date), "day");
                });

                slots = _.filter(slots, function (slot) {
                    return (slot.getStatus() === "granted" || slot.getStatus() === "reserved");
                });

                _.each(slots, function (slot) {
                    slot.set("editable", false);
                });
                row.addSlots(slots);
            }, this);
        }
    });

    ns.IdealizedWeeklyCalendarView = BaseView.extend({
        getInitDate: function () {
            return moment();
        }
    });

}(Flod));
