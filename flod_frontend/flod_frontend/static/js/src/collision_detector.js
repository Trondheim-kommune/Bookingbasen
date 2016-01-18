var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.CollisionSlot = ns.TimeSlot.extend({

        defaults: {
            "status": "collision",
            "editable": false,
            "display_name": "Konflikt"
        },

        initialize: function (data) {
            this.calculate();
        },

        addSlot: function (slot) {
            this.get("slots").push(slot);
            this.calculate();
        },

        calculate: function () {
            var start_time = _.min(this.get("slots"), function (slot) {
                var start_time = slot.get("start_time");
                return start_time.unix();
            });
            var start_date = _.min(this.get("slots"), function (slot) {
                if (slot.has("start_date")) {
                    return moment(slot.get("start_date"), "YYYY-MM-DD").unix();
                } else {
                    return moment(slot.get("start_time").format('YYYY-MM-DD')).unix();
                }
            });
            var end_time = _.max(this.get("slots"), function (slot) {
                var end_time = slot.get("end_time");
                return end_time.unix();
            });
            var end_date = _.max(this.get("slots"), function (slot) {
                if (slot.has("start_date")) {
                    return moment(slot.get("end_date"), "YYYY-MM-DD").unix();
                } else {
                    return moment(slot.get("end_time").format('YYYY-MM-DD')).unix();
                }
            });
            this.set({
                "start_date": (start_date.has("start_date")) ? moment(start_date.get("start_date")) : moment(start_date.get("start_time").format('YYYY-MM-DD')),
                "end_date": (end_date.has("end_date")) ? moment(end_date.get("end_date")) : moment(end_date.get("end_time").format('YYYY-MM-DD')),
                "start_time": moment(start_time.get("start_time")),
                "end_time": moment(end_time.get("end_time")),
                "week_day": end_time.get("week_day")
            });
        },
        addResolveRows: function (rows) {
            _.each(rows, function (row) {
                row.on("slotChanged", this.checkResolve, this);
                row.on("slotRemoved", this.checkResolve, this);
            }, this);
            this.resolveRows = rows;
            this.originalCollection = this.collection;
        },

        checkResolve: function () {
            if (ns.findCollisions(this.get("slots")).length > 1) {
                this.originalCollection.remove(this);
                _.each(this.get("slots"), function (slot) {
                    this.originalCollection.addSlot(slot);
                }, this);
                _.each(this.resolveRows, function (row) {
                    row.destroy();
                });
            }
        },

        getLabel: function() {
            return "";
        },

        close: function () {
            this.set("expanded", false);
            _.each(this.resolveRows, function (row) {
                row.destroy();
            });
        }
    });

    var checkSlotWithinDates = function (slot, collision) {
        var start_date = (slot.has("start_date")) ? moment(slot.get("start_date"), "YYYY-MM-DD") : moment(slot.get("start_time").format('YYYY-MM-DD'));
        var end_date = (slot.has("end_date")) ? moment(slot.get("end_date"), "YYYY-MM-DD") : moment(slot.get("end_time").format('YYYY-MM-DD'));

        var collisionRange = moment().range(collision.get("start_date"), collision.get("end_date"));
        if (collisionRange.contains(start_date)) {
            return true;
        }
        if (collisionRange.contains(end_date)) {
            return true;
        }

        var slotRange = moment().range(start_date, end_date);
        if (slotRange.contains(collision.get("start_date"))) {
            return true;
        }
        if (slotRange.contains(collision.get("end_date"))) {
            return true;
        }

        return false;
    };

    function compare(a, b) {
        if (a.get('start_time').unix() > b.get('start_time').unix()) {
            return -1;
        }
        if (a.get('start_time').unix() < b.get('start_time').unix()) {
            return 1;
        }
        return 0;
    }


    function checkArrangement(collisionSlot) {
        var arrangement = _.find(collisionSlot.get('slots'), function (slot) {
            return slot.get('is_arrangement');
        });
        if (!arrangement) {
            return collisionSlot;
        }
        return arrangement;
    }


    ns.findCollisionsSlots = function (slots) {
        var coll = _.reduce(slots.sort(compare), function (collisions, slot) {
            var added = false;
            _.each(collisions.sort(compare), function (collision) {
                if (checkSlotWithinDates(slot, collision) && collision.collidesWith(slot)) {
                    collision.addSlot(slot);
                    added = true;
                }
            });
            if (!added) {
                collisions.push(new ns.CollisionSlot({"slots": [slot]}));
            }
            return collisions;
        }, []);

        return _.map(coll, function (collision) {
            if (collision.get("slots").length > 1) {
                return checkArrangement(collision);
            } else {
                return collision.get("slots")[0];
            }
        });
    };

    ns.findCollisions = function (mappedSlots) {
        var result = _.reduce(mappedSlots, function (res, slots, key) {
            res[key] = ns.findCollisionsSlots(slots);
            return res;
        }, {});
        return result;
    };

}(Flod));
