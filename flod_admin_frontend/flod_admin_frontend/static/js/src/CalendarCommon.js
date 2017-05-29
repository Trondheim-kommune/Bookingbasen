var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.extendData = function (data, other) {
        var now = new ns.TimeSlot(data);
        other.push(now);
        var start = _.min(other, function (slot) {
            var d = moment(now)
                .hours(slot.get('start_time').hours())
                .minutes(slot.get('start_time').minutes());
            return d.valueOf();
        }).get('start_time');

        var end = _.max(other, function (slot) {
            var d = moment(now)
                .hours(slot.get('end_time').hours())
                .minutes(slot.get('end_time').minutes());
            return d.valueOf();
        }).get('end_time');

        data.start_time.hours(start.hours()).minutes(start.minutes());
        data.end_time.hours(end.hours()).minutes(end.minutes());
        return data;
    };

    ns.SlotClickMixin = {
        slotClicked: function (slot) {

            if (slot instanceof ns.CollisionSlot) {
                this.handleCollisionSlot(slot);
                return;
            }
            if (slot.get("editable")) {
                this.handleSlotSelect(slot);
                return;
            }
            var canRedirect = slot.has("application_id");
            if (canRedirect) {
                window.location.href = "/applications/" + slot.get("application_id");
            }
            canRedirect = slot.has("rammetid_id");
            if (canRedirect) {
                window.location.href = "/rammetid/" + slot.get("rammetid_id");
            }
        },

        handleCollisionSlot: function (slot) {
            if (slot.get("expanded")) {
                slot.close();
            } else {
                var index = this.calendar.getIndexForRow(slot.collection) + 1;
                slot.set("expanded", true);

                var name = slot.getLabel();
                var subSlots = slot.get("slots");
                if (slot.get('is_arrangement') && slot.get("slots") && slot.get('is_arrangement') === true) {
                    name = "Overstyrer";
                    subSlots = _.reject(slot.get("slots"), function (slot) {
                        return slot.get('is_arrangement');
                    });
                }

                slot.addResolveRows(_.map(subSlots, function (originalSlot, i) {
                    originalSlot.parentCollection = slot.collection;
                    var row = new ns.CalendarRow(
                        [originalSlot],
                        {
                            "editable": true,
                            "displayName": name,
                            "conflict": true,
                            "date": slot.get('start_time')
                        }
                    );
                    row.onlyOwn = true;
                    this.calendar.addRow(row, index + i);
                    return row;
                }, this));
            }
        },

        handleSlotSelect: function (slot) {
            slot.set('selected', !slot.get('selected'));

            var selectedSlots = _.filter(this.calendar.getSlots(), function (slot) {
                return slot.get('selected');
            });
            this.trigger("toggleSlotSelect", selectedSlots);
        }
    };

    ns.isAfter = function (end, slot2) {
        var start = moment(slot2.get('start_time').format('HH.mm'), 'HH.mm');
        return end.isSame(start);
    };

    ns.isBefore = function (start, slot2) {
        var end = moment(slot2.get('end_time').format('HH.mm'), 'HH.mm');
        return end.isSame(start);
    };

    ns.isNextTo = function (data, slot) {
        var end = moment(data.end_time.format('HH.mm'), 'HH.mm');
        var start = moment(data.start_time.format('HH.mm'), 'HH.mm');
        return (ns.isAfter(end, slot) || ns.isBefore(start, slot));
    };

    ns.concatSlots = function (slotsa, slotsb) {
        _.each(slotsb, function (value, key) {
            if (_.has(slotsa, key)) {
                slotsa[key] = slotsa[key].concat(value);
            } else {
                slotsa[key] = value;
            }
        });
        return slotsa;
    };

    ns.mapSlots = function (res, slot) {
        var date = slot.get("start_time").format("YYYY-MM-DD");
        if (!res[date]) {
            res[date] = [];
        }
        res[date].push(slot);
        return res;
    };

    ns.mapSlotsByWeekday = function (res, slot) {
        var weekday = slot.get("week_day");
        if (!res[weekday]) {
            res[weekday] = [];
        }
        res[weekday].push(slot);
        return res;
    };

    ns.Slots = Backbone.Collection.extend({

        model: ns.TimeSlot,

        baseUrl: '/api/booking/v1/slots/',

        initialize: function (models, options) {
            this.options = options;
        },

        parse: function (models) {
            _.each(models, function (model) {
                model['display_name'] = model['display_name'] + " (søknad #" + model['application_id'] + ")";
            });
            return models;
        },


        url: function () {
            var params = _.map(this.options, function (value, key) {
                return encodeURIComponent(key) + "=" + encodeURIComponent(value);
            }).join('&');

            return this.baseUrl + '?' + params;
        }
    });

    ns.RepeatingSlots = ns.Slots.extend({
        baseUrl: '/api/booking/v1/slots/repeating/'
    });

    ns.isNextDay = function (time1, time2) {
        var day1 = moment(time1).hours(0).minutes(0);
        var day2 = moment(time2).hours(0).minutes(0);
        return (day1.diff(day2, 'd') !== 0);
    };

    var BlockedSlot = ns.TimeSlot.extend({
        defaults: {
            status: 'reserved',
            display_name: "Enheten har reservert lokalet til eget bruk",
            editable: false
        },
        initialize: function (data) {
            //fix issues with the fact that our calendar doesn't handle spans longer than from
            // 08:00 - 23:00 the same day
            if (data.start_time.hour() === 0 && data.start_time.minute() === 0) {
                this.set('start_time', data.start_time.hour(8));
            }
            if (data.end_time.hour() === 0 && data.end_time.minute() === 0 && ns.isNextDay(data.start_time, data.end_time)) {
                this.set('end_time', data.end_time.hour(23));
            }

        },

        getLabel: function () {
            if (this.get("note")) {
                return this.get("note");
            }
            return ""
        }
    });

    ns.BlockedSlots = Backbone.Collection.extend({

        model: BlockedSlot,

        type: 'blockedtimes',

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

    ns.WeeklyBlockedSlots = ns.BlockedSlots.extend({
        type: 'weeklyblockedtimes'
    });

    ns.RammetidSlot = ns.TimeSlot.extend({
        defaults: {
            status: 'rammetid',
            display_name: "Rammetid",
            editable: false
        }
    });

    ns.RammetidSlots = Backbone.Collection.extend({
        model: ns.RammetidSlot,
        initialize: function (models, options) {
            this.options = options;
            if (!this.options.slot_duration) {
                this.options.slot_duration = 30;
            }
        },
        url: function () {
            var params = _.map(this.options, function (value, key) {
                return encodeURIComponent(key) + "=" + encodeURIComponent(value);
            }).join('&');
            return "/api/booking/v1/weeklyrammetidslots/?" + params;
        }
    });

}(Flod));
