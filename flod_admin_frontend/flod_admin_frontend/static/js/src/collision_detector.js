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
                if (slot.has("start_date")) {
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
                if (slot.has("start_date")) {
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

        updateWeekday: function () {
            // Update slot.week_day if row has changed
            _.chain(this.get("slots"))
                .filter(function (slot) {
                    return this.isRowChanged(slot);
                }, this)
                .each(function (slot) {
                    var weekday = slot.get("end_time").isoWeekday();
                    slot.set("week_day", weekday);
                });
        },

        isRowChanged: function (slot) {
            var isRow = slot.collection instanceof ns.CalendarRow;
            var isConflictRow = slot.collection.options &&
                slot.collection.options.conflict;
            var rowChanged = isRow && !isConflictRow &&
                slot.collection !== this.originalCollection;
            return rowChanged;
        },

        checkResolve: function () {
            this.updateWeekday();
            var collisions = findCollisions(this.get("slots"));
            if (collisions.length > 1) {

                var released = _.filter(collisions, function (sl) {
                    return !(sl instanceof ns.CollisionSlot);
                }, this);

                if (released.length == collisions.length) {
                    //if all collisions are resolved
                    this.originalCollection.remove(this);
                    _.chain(this.get("slots"))
                        .reject(function (slot) {
                            // Skip slots where the collection has changed.
                            // The collection will change if a slot is moved to a
                            // new row (day)

                            slot.parentCollection = null;
                            return this.isRowChanged(slot);
                        }, this)
                        .each(function (slot) {
                            this.originalCollection.addSlot(slot);
                        }, this);

                    _.each(this.resolveRows, function (row) {
                        row.destroy();
                    });
                } else {
                    //a part of collision is resolved
                    this.originalCollection.remove(this);
                    _.each(released, function (collision) {
                        var found = false;

                        _.each(this.resolveRows, function (row) {
                            if (row.length == 0) {
                                row.destroy();
                            } else if (row.get(collision)) {
                                this.originalCollection.addSlot(collision);

                                row.destroy();
                                found = true;
                                return;
                            }
                        }, this);

                        if (!found) {
                            collision.parentCollection = null;
                        }
                    }, this);

                    this.removeSlots(released);

                    this.originalCollection.add(this);
                }
            } else if (collisions.length == 1) {
                this.originalCollection.remove(this);
                this.calculate();
                this.originalCollection.add(this);
            }
        },

        getLabel: function () {
            return this.get('display_name');
        },

        removeSlots: function (deleteList) {
            if (deleteList.length > 0) {
                var newslots = _.filter(this.get('slots'), function (sl) {
                    return !_.contains(deleteList, sl);
                }, this);
                this.set('slots', newslots);
                this.calculate();
            }
        },

        close: function () {
            this.set("expanded", false);
            _.each(this.resolveRows, function (row) {
                row.destroy();
            });

            this.resolveRows = null;
        }
    });

    var checkSlotWithinDates = function (slot, collision) {
        var start_date = (slot.has("start_date"))
            ? moment(slot.get("start_date"), "YYYY-MM-DD")
            : moment(slot.get("start_time").format('YYYY-MM-DD'));
        var end_date = (slot.has("end_date"))
            ? moment(slot.get("end_date"), "YYYY-MM-DD")
            : moment(slot.get("end_time").format('YYYY-MM-DD'));

        var collisionRange = moment().range(
            collision.get("start_date"),
            collision.get("end_date")
        );
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
        return slotRange.contains(collision.get("end_date"));
    };

    function compare(a, b) {
        if (a.get('start_time').unix() > b.get('start_time').unix()) {
            return 1;
        }
        if (a.get('start_time').unix() < b.get('start_time').unix()) {
            return -1;
        }
        return 0;
    }

    function checkArrangement(collisionSlot) {
        var arrangement = _.find(collisionSlot.get('slots'), function (slot) {
            return slot.get('is_arrangement');
        });
        if (arrangement) {
            _.each(arrangement.attributes, function (value, key) {
                collisionSlot.set(key, value);
            });

            collisionSlot.set('status', arrangement.get("status"));
            collisionSlot.set(
                'display_name',
                arrangement.get('display_name') + '\nArrangement'
            );
        }
        return collisionSlot;
    }

    var findCollisions = function (slots) {
        var coll = _.reduce(slots.sort(compare), function (collisions, slot) {
            var added = false;
            _.each(collisions.sort(compare), function (collision) {
                var collides = checkSlotWithinDates(slot, collision) &&
                    collision.collidesWith(slot);

                if (collides) {
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
        return _.reduce(mappedSlots, function (res, slots, key) {
            res[key] = findCollisions(slots);
            return res;
        }, {});
    };

    ns.OverlappingSlot = ns.CollisionSlot.extend({

        defaults: {
            "status": "overlapping",
            "editable": false,
            "display_name": "Overlappende"
        }
    });

    var findOverlapping = function (slots) {
        var coll = _.reduce(slots.sort(compare), function (collisions, slot) {
            var added = false;
            _.each(collisions.sort(compare), function (collision) {
                var collides = slot.get('week_day') === collision.get('week_day') &&
                    collision.collidesWith(slot);

                if (collides) {
                    collision.addSlot(slot);
                    added = true;
                }
            });
            if (!added) {
                collisions.push(new ns.OverlappingSlot({"slots": [slot]}));
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

    ns.findOverlapping = function (mappedSlots) {
        return _.reduce(mappedSlots, function (res, slots, key) {
            res[key] = findOverlapping(slots);
            return res;
        }, {});
    };
}(Flod));
