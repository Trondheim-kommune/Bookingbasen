var Flod = window.Flod || {};
Flod.calendar = Flod.calendar || {};

(function (ns, undefined) {
    "use strict";

    function createSlot(start_time, end_time, week_day) {
        return new Flod.TimeSlot({
            "start_time": start_time,
            "end_time": end_time,
            "week_day": week_day,
            "editable": false,
            "status": "reserved"
        });
    }

    function invertDay(day, slots) {

        slots = _.sortBy(slots, function (slot) {
            return slot.get('start_time').unix();
        });

        var test = _.map(slots, function (slot) {
            return [slot.get("start_time"), slot.get("end_time")];
        });

        test.unshift([moment("08:00", "HH:mm"), moment("08:00", "HH:mm")]);
        test.push([moment("23:00", "HH:mm"), moment("23:00", "HH:mm")]);

        return _.compact(_.map(test, function (span1, index, array) {
            if (array[index + 1]) {
                var span2 = array[index + 1];
                var start = span1[1];
                var end = span2[0];
                if (start.diff(end) !== 0) {
                    return createSlot(start, end, day);
                }
            }
        }));
    }

    /*
        input: a dict with the following structure
        {
            week_day: [slot, ..],
            week_day2: [slot, ..]
        }
        where week_day is an int (isoweekday) and slot is a TimeSlot

        returns a similar structure, but "inverted", i.e the slots are now free, and the free slots are filled
     */
    ns.invertSlots = function (slotDict) {

        return _.reduce(_.range(1, 8), function (res, day) {
            res[day] = invertDay(day, slotDict[day]);
            return res;
        }, {});
    };

    var subtract = function (source, target) {
        var clone = source.clone();

        var sameStart = clone.get('start_time').isSame(target.get('start_time'));
        var sameEnd = clone.get('end_time').isSame(target.get('end_time'));

        if (sameStart && sameEnd) {
            return null;
        }
        if (sameStart) {
            clone.set('start_time', moment(target.get('end_time')));
            return [clone];
        }
        if (sameEnd) {
            clone.set('end_time', moment(target.get('start_time')));
            return [clone];
        }
        if (clone.get('start_time').isBefore(target.get('start_time')) && clone.get('end_time').isAfter(target.get('end_time'))) {

            var clone2 = clone.clone();
            clone.set('end_time', target.get('start_time'));
            clone2.set('start_time', target.get('end_time'));
            return [clone, clone2];
        }
        if (target.get('start_time').isBefore(clone.get('start_time'))) {
            clone.set('start_time', target.get('end_time'));
            return [clone];
        }

        if (target.get('end_time').isAfter(clone.get('end_time'))) {
            clone.set('end_time', target.get('start_time'));
            return [clone];
        }

        return [source];
    };

    function compare(a, b) {
        if (a.get('start_time').unix() < b.get('start_time').unix()) {
            return -1;
        }
        if (a.get('start_time').unix() > b.get('start_time').unix()) {
            return 1;
        }
        return 0;
    }

    ns.splitSlot = function (toSplit, splitWith) {
        splitWith.sort(compare);
        var check = [toSplit];
        _.each(splitWith, function (split) {
            var target = check.shift();
            if (target.collidesWith(split)) {
                var res = subtract(target, split);
                _.each(res, function (r) {
                    check.unshift(r);
                });
            } else {
                check.unshift(target);
            }
        });
        return _.compact(check).reverse();
    };

}(Flod.calendar));