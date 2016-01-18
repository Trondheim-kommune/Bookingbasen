var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    function parseTime(string) {
        var time = moment(string);
        if (time.isValid()) {
            return time;
        }
        return moment(string, "HH:mm:ss");
    }

    ns.ColorSlot = Backbone.Model.extend({
        defaults: {
            "start_time": null,
            "end_time": null,
            "background_color": "#FFFFFF"
        },
        parse: function (attributes) {
            if (attributes) {
                var data = _.clone(attributes);
                if (data.start_time) {
                    data.start_time = parseTime(data.start_time);
                }
                if (data.end_time) {
                    data.end_time = parseTime(data.end_time);
                }
                return data;
            }
            return null;
        }
    });

    var ColorRow = Backbone.Collection.extend({
        model: ns.ColorSlot,
        getByTime: function (time) {
            return this.find(function (slot) {
                var start_time = moment(slot.get("start_time").format("HH:mm"), "HH:mm");
                var end_time = moment(slot.get("end_time").format("HH:mm"), "HH:mm");
                return ((start_time.isBefore(time) || start_time.isSame(time)) && end_time.isAfter(time));
            });
        }
    });

    ns.CalendarRow = Backbone.Collection.extend({

        model: ns.TimeSlot,

        initialize: function (models, options) {
            this.displayName = options.displayName;
            this.date = moment(options.date);
            this.options = _.omit(options, "displayName", "date");
            this.colors = new ColorRow(this.options.colors || [], {parse: true});
        },

        reset: function (models, options) {
            Backbone.Collection.prototype.reset.apply(this, arguments);
            this.each(this.checkEditable, this);
            return this;
        },

        removeSlot: function (slot) {
            this.remove(slot);
            this.trigger("slotRemoved");
        },

        getDisplayName: function () {
            return this.displayName || "";
        },

        getDate: function () {
            return this.date;
        },

        checkEditable: function (slot) {
            if (_.isUndefined(slot.get("editable")) || slot.get("editable")) {
                slot.set({"editable": this.options.editable});
            }
        },

        slotCollides: function (slot) {

            var collisions = this.map(function (existing) {
                return existing.collidesWith(slot);
            });
            return collisions.indexOf(true) !== -1;
        },

        canChangeSlotTo: function (slot, start_time, end_time) {

            if (this.onlyOwn && (slot.collection !== this)) {
                return false;
            }

            var cloned = slot.clone();

            var start = moment(this.date)
                .hours(start_time.hours())
                .minutes(start_time.minutes());

            var end = moment(this.date)
                .hours(end_time.hours())
                .minutes(end_time.minutes());

            cloned.set({"start_time": start});
            cloned.set({"end_time": end});

            //check if it is a conflict slot and compare with slots on parent row
            if (this.onlyOwn && slot.parentCollection){

                var collidesWithOtherSlots = false;

                for (var i in slot.parentCollection.models) {
                    var parentRowSlot = slot.parentCollection.models[i];
                    if (parentRowSlot.collidesWith(cloned)){

                        collidesWithOtherSlots = _.flatten(_.filter(parentRowSlot.get('slots'), function (sl) {
                            return (sl.cid == slot.cid);
                        }, this)).length == 0;

                        if (collidesWithOtherSlots){
                            break;
                        }
                    }
                }

                return !collidesWithOtherSlots;
            }

            if (this.slotCollides(cloned)) {

                var collisions = this.filter(function (existing) {
                    return existing.collidesWith(cloned);
                });
                if (collisions.length < 2) {
                    return _.isEqual(collisions[0], slot);
                } else {
                    return false;
                }
            }
            return true;
        },


        addColors: function (slots) {
            var status = _.map(slots, function (slot) {
                this.addColor(slot);
            }, this);
            return (status.indexOf(false) === -1);
        },

        addColor: function (slot) {
            if (!(slot instanceof ns.ColorSlot)) {
                slot = new ns.ColorSlot(slot, {
                    parse: true
                });
            }
            this.colors.add(slot);
        },

        addSlots: function (slots) {
            var status = _.map(slots, function (slot) {
                this.addSlot(slot);
            }, this);
            return (status.indexOf(false) === -1);
        },

        addSlot: function (slot) {

            if (!(slot instanceof ns.TimeSlot)) {
                slot = new ns.TimeSlot(slot);
            }

            if (slot.collection && _.isEqual(slot.collection, this)) {
                this.trigger("slotChanged", slot);
                return true;
            }

            if (this.slotCollides(slot.clone().changeDate(this.getDate()))) {
                return false;
            }

            if (slot.get('slots')){
                var self = this;
                _.each(slot.get('slots'), function(collisionslot){
                        collisionslot.changeDate(self.getDate());
                    }
                );
            }

            slot.changeDate(this.getDate());
            var prev;
            if (slot.collection) {
                prev = slot.collection;
                prev.remove(slot);
            }
            this.checkEditable(slot);
            this.add(slot);

            if (prev) {
                prev.trigger("slotRemoved");
            }

            return true;
        },

        getByStart: function (time) {
            return this.find(function (slot) {
                return moment(
                    slot.get("start_time").format("HH:mm"),
                    "HH:mm"
                ).isSame(time);
            });
        },

        timeOccupied: function (time) {
            return !!this.find(function (slot) {
                var start = moment(
                    slot.get("start_time").format("HH:mm"),
                    "HH:mm"
                );
                var end = moment(
                    slot.get("end_time").format("HH:mm"),
                    "HH:mm"
                );
                if (moment().range(start, end).contains(time)) {
                    if (!start.isSame(time) && !end.isSame(time)) {
                        return true;
                    }
                }
                return false;
            });
        },

        getAvailableSpan: function (start) {
            var slots_after = this.filter(function (slot) {
                return (slot.get("start_time").diff(start) > 0);
            });
            if (slots_after.length) {
                var next = _.min(slots_after, function (slot) {
                    return slot.get("start_time").format("X");
                });
                return moment(next.get("start_time"));
            }
            return moment(this.date)
                .hours(this.options.calendar_end.hours())
                .minutes(this.options.calendar_end.minutes())
                .seconds(0);
        },

        destroy: function () {
            this.reset();
            this.trigger("destroy", this);
        }

    });
}(Flod));