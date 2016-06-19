var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var EmptySlotClickMixIn = {
        emptySlotClick: function (data) {
            var row = data.row;

            data = _.extend(_.omit(data, "row"), {
                "application": this.model.get('id'),
                "person": this.model.get('person'),
                "organisation": this.model.get('organisation'),
                "resource": this.model.get('resource'),
                "status": this.model.get("status") + " own-slot",
                "start_date": this.model.get('type') === 'repeating' ? this.model.get("slots")[0].start_date : null,
                "end_date": this.model.get('type') === 'repeating' ? this.model.get("slots")[0].end_date : null
            });

            //check to see if this slot can be merged with other new ones
            var other = row.filter(function (slot) {
                return (slot.get('status').indexOf("own-slot") >= 0) && ns.isNextTo(data, slot);
            });
            if (other.length) {
                data = ns.extendData(data, other);
                _.each(other, function (slot) {
                    row.removeSlot(slot);
                });
            }

            row.addSlot(new ns.TimeSlot(data));
            this.trigger("slotAdded");
        }
    };

    ns.RepeatingCalendarView = ns.IdealizedWeeklyCalendarView.extend({

        initialize: function () {
            ns.IdealizedWeeklyCalendarView.prototype.initialize.apply(this, arguments);
            this.calendar.on("slotClick", this.slotClicked, this);
        },

        render: function () {
            ns.IdealizedWeeklyCalendarView.prototype.render.apply(this, arguments);
            this.addSlots();
            return this;
        },

        addSlots: function () {
            //do nothing
        },

        getData: function () {
            var relevantSlots = [];
            _.each(this.calendar.getSlots(), function (slot) {
                if (slot instanceof ns.CollisionSlot && !slot.get('expanded')){
                    relevantSlots.push(_.filter(slot.get('slots'), function (conflictslot) {
                        return (conflictslot.get("application") === this.model.get("id"));
                    }, this));

                } else if (slot.get("application") === this.model.get("id")){
                    relevantSlots.push(slot);
                }
            }, this);

            return _.flatten(relevantSlots);
        },

        getSlots: function () {
            return this.getData().map(function (slot) {
                return {
                    start_time: slot.get('start_time').format("HH:mm:ss"),
                    end_time: slot.get('end_time').format("HH:mm:ss"),
                    start_date: slot.get('start_date'),
                    end_date: slot.get('end_date'),
                    id: slot.get('id'),
                    week_day: slot.get('start_time').isoWeekday()
                };
            });
        },

        resetRows: function () {

            this.calendarView.model.reset(
                _.map(this.getDays(this.getInitDate()), function (day) {
                    return {"displayName": day.moment.format("dddd"), "date": day.moment};
                })
            );

            var dates = {
                start_date: this.model.get("slots")[0].start_date,
                end_date: this.model.get("slots")[0].end_date
            };

            var rammetidSlots = new ns.RammetidSlots([], {
                resource_uri: this.options.data.resource.get("uri"),
                start_date: moment(dates.start_date).format("YYYY-MM-DD"),
                end_date: moment(dates.end_date).format("YYYY-MM-DD"),
                split_by_slots: true,
                slot_duration: 30
            });

            var slots = new ns.RepeatingSlots([], {
                resource_uri: this.options.data.resource.get("uri"),
                start_date: moment(dates.start_date).format("YYYY-MM-DD"),
                end_date: moment(dates.end_date).format("YYYY-MM-DD"),
                except: this.model.get("id"),
                slot_duration: 30
            });

            var blocked = new ns.WeeklyBlockedSlots([], {
                "resource_uri": this.options.data.resource.get("uri"),
                start_date: moment(dates.start_date).format("YYYY-MM-DD"),
                end_date: moment(dates.end_date).format("YYYY-MM-DD"),
                slot_duration: 30
            });

            var showSlots = _.after(3, _.bind(function () {
                this.slotsFectched(slots, blocked, rammetidSlots);
            }, this));

            slots.fetch({"success": showSlots});
            blocked.fetch({"success": showSlots});
            rammetidSlots.fetch({"success": showSlots});
        },

        slotsFectched: function (slots, blocked, rammetidSlots) {
            // Show own slots with stripes in the calendar.
            var ownSlots = this.model.getSlots();
            _.each(ownSlots, function (slot) {
                slot.set({
                    status: slot.get('status') + ' own-slot'
                });
            });
            slots.each(function (slot) {
                var status = (slot.get('status') === "Granted") ? "Granted" : 'other';
                slot.set({
                    'editable': false,
                    'status': status
                });
            });

            var mappedSlots = slots.reduce(ns.mapSlotsByWeekday, {});
            var mappedBlocked = blocked.reduce(ns.mapSlotsByWeekday, {});
            var mappedOwnSlots = ownSlots.reduce(ns.mapSlotsByWeekday, {});
            mappedSlots = ns.concatSlots(mappedSlots, mappedOwnSlots);
            var mappedSlotsWithBlocked = ns.findCollisions(ns.concatSlots(mappedSlots, mappedBlocked));
            _.each(mappedSlotsWithBlocked, function (slots, weekday) {
                var row = this.calendar.getRowForWeekday(weekday);
                if (row) {
                    row.addSlots(slots);
                }
            }, this);

            var mappedRammetidSlots = rammetidSlots.reduce(ns.mapSlotsByWeekday, {});
            _.each(mappedRammetidSlots, function (slots, weekday) {
                this.calendar.getRowForWeekday(weekday).addSlots(slots);
            }, this);
        }
    });

    _.extend(ns.RepeatingCalendarView.prototype,  ns.SlotClickMixin);
    _.extend(ns.RepeatingCalendarView.prototype, EmptySlotClickMixIn);

    ns.SingleCalendarView = ns.BrowsableWeeklyCalendarView.extend({

        initialize: function () {
            ns.BrowsableWeeklyCalendarView.prototype.initialize.apply(this, arguments);
            this.calendar.on("slotClick", this.slotClicked, this);
        },

        resetRows: function () {
            var days = this.currentWeek.getDays();
            this.calendar.reset(
                _.map(days, function (day) {
                    return {
                        "displayName": day.moment.format("dddd DD.MM"),
                        "date": day.moment
                    };
                })
            );

            var rammetidSlots = new ns.RammetidSlots([], {
                resource_uri: this.options.data.resource.get("uri"),
                "start_date": days[0].moment.format("YYYY-MM-DD"),
                "end_date": days[days.length - 1].moment.format("YYYY-MM-DD"),
                split_by_slots: true,
                split_by_arrangement_slots: true,
                slot_duration: 30
            });

            var slots = new ns.Slots([], {
                resource_uri: this.model.get("resource").uri,
                year: this.currentWeek.get("year"),
                week: this.currentWeek.get("week"),
                except: this.model.get("id"),
                slot_duration: 30
            });

            var blocked = new ns.BlockedSlots([], {
                "resource_uri": this.options.data.resource.get("uri"),
                "start_date": days[0].moment.format("YYYY-MM-DD"),
                "end_date": days[days.length - 1].moment.format("YYYY-MM-DD"),
                slot_duration: 30
            });
            var showSlots = _.after(3, _.bind(function () {
                this.slotsFectched(slots, blocked, rammetidSlots);
            }, this));

            slots.fetch({"success": showSlots});
            blocked.fetch({"success": showSlots});
            rammetidSlots.fetch({"success": showSlots});
        },

        slotsFectched: function (slots, blocked, rammetidSlots) {
            var mappedRammetidSlots = rammetidSlots.reduce(ns.mapSlotsByWeekday, {});
            mappedRammetidSlots = _.reduce(mappedRammetidSlots, function (res, slots, week_day) {
                // Convert to date format to simplify concat
                var date = this.calendar.getRowForWeekday(week_day).date;
                // Update dates as these may be wrong
                _.each(slots, function (slot) {
                    slot.changeDate(date);
                });
                res[date.format('YYYY-MM-DD')] = slots;
                return res;
            }, {}, this);

            var mappedSlots = slots.reduce(ns.mapSlots, {});

            // Show own slots with stripes in the calendar.
            var ownSlots = this.model.getSlots();
            var self = this;

            _.each(ownSlots, function (slot) {
                slot.set({
                    status: slot.get('status') + ' own-slot',
                    is_arrangement: self.model.get("is_arrangement"),
                    display_name: slot.getDisplayName()
                });
            });
            var mappedOwnSlots = ownSlots.reduce(ns.mapSlots, {});
            var combinedWithOwn = ns.findCollisions(ns.concatSlots(mappedSlots, mappedOwnSlots));

            var combined = ns.concatSlots(combinedWithOwn, mappedRammetidSlots);
            var mappedBlocked = blocked.reduce(ns.mapSlots, {});
            // "chop off" unwanted parts from blocked time
            mappedBlocked = _.reduce(mappedBlocked, function (res, slots, day) {
                var match = combined[day];
                if (match) { // If there are other slots for this day, check split
                    res[day] = _.flatten(_.map(slots, function (slot) {
                        return ns.calendar.splitSlot(slot, match);
                    }));
                } else { // Use as is
                    res[day] = slots;
                }
                return res;
            }, {});

            // Arrangements should be able to steal time from existing applications,
            // therefore instead of adding slots we just coloring the calendar.
            if (this.model.get("is_arrangement") && this.model.get("status") !== "Granted") {
                _.each(mappedOwnSlots, function (slots, date) {
                    var row = this.calendar.getRowForDate(moment(date));
                    if (row) {
                        row.addSlots(slots);
                    }
                }, this);
                _.each(ns.concatSlots(combined, mappedBlocked), function (slots, date) {
                        var colors = _.map(slots, function (slot) {
                            var color = "gray";
                            if (slot.get('status') === "Granted") {
                                color = "#468847";
                            }
                            if (slot.get('status') === "collision") {
                                color = "#F0AD4E";
                            }
                            if (slot.get('status') === "rammetid") {
                                color = "#336699";
                            }
                            if (slot.get('status') === "Pending own-slot" ||
                                slot.get('status') === "Processing own-slot") {
                                color = "white";
                            }
                            return {
                                "start_time": slot.get("start_time"),
                                "end_time": slot.get("end_time"),
                                "background_color": color
                            };
                        });
                        this.calendar.getRowForDate(moment(date)).addColors(colors);
                    }, this);
            } else {
                slots.each(function (slot) {
                    var status = (slot.get('status') === "Granted") ? "Granted" : 'other';
                    slot.set({
                        editable: false,
                        status: status
                    });
                });
                _.each(ns.concatSlots(combined, mappedBlocked), function (slots, date) {
                    var row = this.calendar.getRowForDate(moment(date));
                    if (row) {
                        row.addSlots(slots);
                    }
                }, this);
            }
        },

        render: function () {
            ns.BrowsableWeeklyCalendarView.prototype.render.apply(this, arguments);
            this.addSlots();
            return this;
        },

        addSlots: function () {
           //do nothing
        },

        getData: function () {
            return _.filter(this.calendar.getSlots(), function (slot) {
                return (slot.get("application") === this.model.get("id"));
            }, this);
        },

        getSlots: function () {
            return this.getData().map(function (slot) {
                return {
                    start_time: slot.get('start_time').format("YYYY-MM-DDTHH:mm:ss"),
                    end_time: slot.get('end_time').format("YYYY-MM-DDTHH:mm:ss"),
                    id: slot.get('id')
                };
            });
        }
    });

    _.extend(ns.SingleCalendarView.prototype, ns.SlotClickMixin);
    _.extend(ns.SingleCalendarView.prototype, EmptySlotClickMixIn);

}(Flod));