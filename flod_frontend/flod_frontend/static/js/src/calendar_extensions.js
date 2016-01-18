var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var hsvToRgb = function (h, s, v) {
        var r, g, b;

        var i = Math.floor(h * 6);
        var f = h * 6 - i;
        var p = v * (1 - s);
        var q = v * (1 - f * s);
        var t = v * (1 - (1 - f) * s);

        switch (i % 6) {
        case 0: r = v, g = t, b = p; break;
        case 1: r = q, g = v, b = p; break;
        case 2: r = p, g = v, b = t; break;
        case 3: r = p, g = q, b = v; break;
        case 4: r = t, g = p, b = v; break;
        case 5: r = v, g = p, b = q; break;
        }

        return [r * 255, g * 255, b * 255];
    };


    function getNumberFromString(string) {
        return _.reduce(string, function (acc, char) {
            return acc + char.charCodeAt(0);
        }, 0) % 3000 / 3000;
    }


    var colorGenerator = function () {
        var golden_ratio_conjugate = 0.618033988749895;
        return function (string) {
            var h = getNumberFromString(string);
            h += golden_ratio_conjugate;
            h %= 1;
            var rgb = hsvToRgb(h, 0.7, 0.8);
            var hex = rgb.map(function (i) {
                var v = Math.round(i).toString(16);
                return i < 16 ? '0' + v : v;
            }).join('');
            return '#' + hex;
        };
    };


    var colorGen = colorGenerator();
    var mapNormalSlots = function (res, slot) {
        slot.set('color', colorGen(slot.get('display_name')));
        return ns.mapSlots(res, slot);
    }


    function getColors(mappedSlots) {

        return _.chain(mappedSlots)
            .map(function (value, key) {
                //console.log(value);
                return _.map(value, function (value, key) {
                    return value;
                });
            })
            .flatten()
            .reduce(function (acc, slot) {
                acc[slot.get('display_name')] = slot.get('color');
                return acc;
            }, {})
            .value();
    }


    ns.RepeatingCalendar = ns.IdealizedWeeklyCalendarView.extend({

        initialize: function () {
            ns.IdealizedWeeklyCalendarView.prototype.initialize.apply(this, arguments);
            this.calendar.on("slotClick", this.slotClicked, this);
            this.calendarView.on("slotRemoved", this.slotRemoved, this);
        },

        slotRemoved: function() {
            this.trigger("slotRemoved");
        },

        resetRows: function () {
            ns.IdealizedWeeklyCalendarView.prototype.resetRows.apply(this, arguments);
        },

        setDates: function (dates) {

            _.each(this.calendar.getSlots(), function (slot) {
                if (slot.get('editable') === false) {
                    slot.collection.remove(slot);
                }
            });

            var rammetidSlots = new ns.RammetidSlots([], {
                resource_uri: this.options.data.resource.get("uri"),
                start_date: moment(dates.start_date).format("YYYY-MM-DD"),
                end_date: moment(dates.end_date).format("YYYY-MM-DD"),
                split_by_slots: true
            });

            var slots = new ns.RepeatingSlots([], {
                resource_uri: this.options.data.resource.get("uri"),
                start_date: moment(dates.start_date).format("YYYY-MM-DD"),
                end_date: moment(dates.end_date).format("YYYY-MM-DD"),
                status: "Granted"
            });

            var blocked = new ns.WeeklyBlockedSlots([], {
                "resource_uri": this.options.data.resource.get("uri"),
                start_date: moment(dates.start_date).format("YYYY-MM-DD"),
                end_date: moment(dates.end_date).format("YYYY-MM-DD")
            });

            var showSlots = _.after(3, _.bind(function () {
                this.slotsFectched(slots, blocked, rammetidSlots);
            }, this));

            slots.fetch({"success": showSlots});
            blocked.fetch({"success": showSlots});
            rammetidSlots.fetch({"success": showSlots});
        },

        slotsFectched: function (slots, blocked, rammetidSlots) {
            var mappedSlots = slots.reduce(ns.mapSlotsByWeekday, {});
            var mappedBlocked = blocked.reduce(ns.mapSlotsByWeekday, {});
            _.each(ns.concatSlots(ns.findCollisions(mappedSlots), mappedBlocked), function (slots, weekday) {
                _.each(slots, function (slot) {
                    slot.set({
                        editable: false
                    });
                });
                this.calendar.getRowForWeekday(weekday).addSlots(slots);
            }, this);
            var mappedRammetidSlots = rammetidSlots.reduce(ns.mapSlotsByWeekday, {});
            _.each(mappedRammetidSlots, function (slots, weekday) {
                this.calendar.getRowForWeekday(weekday).addSlots(slots);
            }, this);

            this.fetched = true;
            this.trigger("otherFetched");
        }
    });

    ns.SingleCalendar = ns.BrowsableWeeklyCalendarView.extend({

        initialize: function () {
            ns.BrowsableWeeklyCalendarView.prototype.initialize.apply(this, arguments);
            this.calendar.on("slotClick", this.slotClicked, this);
            this.calendarView.on("slotRemoved", this.slotRemoved, this);
        },

        slotRemoved: function() {
            this.trigger("slotRemoved");
        },

        resetRows: function () {

            var days = this.currentWeek.getDays();
            this.trigger("resetRows", days);

            var rammetidSlots = new ns.RammetidSlots([], {
                resource_uri: this.options.data.resource.get("uri"),
                "start_date": days[0].moment.format("YYYY-MM-DD"),
                "end_date": days[days.length - 1].moment.format("YYYY-MM-DD"),
                split_by_slots: true,
                split_by_arrangement_slots: true
            });

            var slots = new ns.Slots([], {
                resource_uri: this.options.data.resource.get("uri"),
                year: this.currentWeek.get("year"),
                week: this.currentWeek.get("week"),
                status: "Granted"
            });

            var blocked = new ns.BlockedSlots([], {
                "resource_uri": this.options.data.resource.get("uri"),
                "start_date": days[0].moment.format("YYYY-MM-DD"),
                "end_date": days[days.length - 1].moment.format("YYYY-MM-DD")
            });
            var showSlots = _.after(3, _.bind(function () {
                this.slotsFectched(slots, blocked, rammetidSlots);
            }, this));

            slots.fetch({"success": showSlots});
            blocked.fetch({"success": showSlots});
            rammetidSlots.fetch({"success": showSlots});
        },

        slotsFectched: function (slots, blocked, rammetidSlots) {

            var mappedSlots =  slots.reduce(mapNormalSlots, {});
            this.colorMap = getColors(mappedSlots);
            var mappedRammetidSlots = rammetidSlots.reduce(ns.mapSlotsByWeekday, {});
            mappedRammetidSlots = _.reduce(mappedRammetidSlots, function (res, slots, week_day) {
                //convert to date format to simplify concat
                var date = this.calendar.getRowForWeekday(week_day).date;
                //update dates as these may be wrong
                _.each(slots, function (slot) {
                    slot.changeDate(date);
                });
                res[date.format('YYYY-MM-DD')] = slots;
                return res;
            }, {}, this);

            //combine booked slots and rammetid
            var combined = ns.concatSlots(ns.findCollisions(mappedSlots), mappedRammetidSlots);

            var mappedBlocked = blocked.reduce(ns.mapSlots, {});

            //"chop off" unwanted parts from blocked time
            mappedBlocked = _.reduce(mappedBlocked, function (res, slots, day) {
                var match = combined[day];
                if (match) { //if there are other slots for this day, check split
                    res[day] = _.flatten(_.map(slots, function (slot) {
                        return ns.calendar.splitSlot(slot, match);
                    }));
                } else { //use as is
                    res[day] = slots;
                }
                return res;
            }, {});

            _.each(ns.concatSlots(combined, mappedBlocked), function (slots, date) {
                var row = this.calendar.getRowForDate(moment(date));
                _.each(slots, function (slot) {
                    slot.set({
                        editable: false
                    });
                });
                row.addSlots(slots);
            }, this);

            this.trigger("loadedSlots");
        }
    });

}(Flod));
