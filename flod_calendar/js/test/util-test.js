(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('util invert test', {

        "should invert empty dict": function () {
            var slots = {};
            var inverted = Flod.calendar.invertSlots(slots);
            _.each(_.range(1, 8), function (day) {
                assert.equals(inverted[day].length, 1);
                assert.equals(inverted[day][0].get("start_time").format("HH:mm"), "08:00");
                assert.equals(inverted[day][0].get("end_time").format("HH:mm"), "23:00");
                assert.equals(inverted[day][0].get("week_day"), day);
            });
        },

        "should invert dict with full day": function () {
            var slots = {"1": [new Flod.TimeSlot({
                "start_time": "08:00:00",
                "end_time": "23:00:00",
                "week_day": 1
            })]};
            var inverted = Flod.calendar.invertSlots(slots);
            assert.equals(inverted["1"].length, 0);
            _.each(_.range(2, 8), function (day) {
                assert.equals(inverted[day].length, 1);
                assert.equals(inverted[day][0].get("start_time").format("HH:mm"), "08:00");
                assert.equals(inverted[day][0].get("end_time").format("HH:mm"), "23:00");
                assert.equals(inverted[day][0].get("week_day"), day);
            });
        },

        "should invert dict with half day": function () {
            var slots = {"1": [new Flod.TimeSlot({
                "start_time": "08:00:00",
                "end_time": "10:00:00",
                "week_day": 1
            })]};
            var inverted = Flod.calendar.invertSlots(slots);
            assert.equals(inverted["1"].length, 1);

            assert.equals(inverted["1"][0].get("start_time").format("HH:mm"), "10:00");
            assert.equals(inverted["1"][0].get("end_time").format("HH:mm"), "23:00");
            assert.equals(inverted["1"][0].get("week_day"), 1);

            _.each(_.range(2, 8), function (day) {
                assert.equals(inverted[day].length, 1);
                assert.equals(inverted[day][0].get("start_time").format("HH:mm"), "08:00");
                assert.equals(inverted[day][0].get("end_time").format("HH:mm"), "23:00");
                assert.equals(inverted[day][0].get("week_day"), day);
            });
        },

        "should invert dict several slots": function () {
            var slots = {"1": [
                new Flod.TimeSlot({
                    "start_time": "10:00:00",
                    "end_time": "12:00:00",
                    "week_day": 1
                }),
                new Flod.TimeSlot({
                    "start_time": "14:00:00",
                    "end_time": "18:00:00",
                    "week_day": 1
                })
            ]};
            var inverted = Flod.calendar.invertSlots(slots);
            assert.equals(inverted["1"].length, 3);

            assert.equals(inverted["1"][0].get("start_time").format("HH:mm"), "08:00");
            assert.equals(inverted["1"][0].get("end_time").format("HH:mm"), "10:00");
            assert.equals(inverted["1"][0].get("week_day"), 1);

            assert.equals(inverted["1"][1].get("start_time").format("HH:mm"), "12:00");
            assert.equals(inverted["1"][1].get("end_time").format("HH:mm"), "14:00");
            assert.equals(inverted["1"][1].get("week_day"), 1);

            assert.equals(inverted["1"][2].get("start_time").format("HH:mm"), "18:00");
            assert.equals(inverted["1"][2].get("end_time").format("HH:mm"), "23:00");
            assert.equals(inverted["1"][2].get("week_day"), 1);

            _.each(_.range(2, 8), function (day) {
                assert.equals(inverted[day].length, 1);
                assert.equals(inverted[day][0].get("start_time").format("HH:mm"), "08:00");
                assert.equals(inverted[day][0].get("end_time").format("HH:mm"), "23:00");
                assert.equals(inverted[day][0].get("week_day"), day);
            });
        },

        "should invert dict with neighbour slots": function () {
            var slots = {"1": [
                new Flod.TimeSlot({
                    "start_time": "10:00:00",
                    "end_time": "12:00:00",
                    "week_day": 1
                }),
                new Flod.TimeSlot({
                    "start_time": "12:00:00",
                    "end_time": "18:00:00",
                    "week_day": 1
                })
            ]};
            var inverted = Flod.calendar.invertSlots(slots);
            assert.equals(inverted["1"].length, 2);

            assert.equals(inverted["1"][0].get("start_time").format("HH:mm"), "08:00");
            assert.equals(inverted["1"][0].get("end_time").format("HH:mm"), "10:00");
            assert.equals(inverted["1"][0].get("week_day"), 1);

            assert.equals(inverted["1"][1].get("start_time").format("HH:mm"), "18:00");
            assert.equals(inverted["1"][1].get("end_time").format("HH:mm"), "23:00");
            assert.equals(inverted["1"][1].get("week_day"), 1);

            _.each(_.range(2, 8), function (day) {
                assert.equals(inverted[day].length, 1);
                assert.equals(inverted[day][0].get("start_time").format("HH:mm"), "08:00");
                assert.equals(inverted[day][0].get("end_time").format("HH:mm"), "23:00");
                assert.equals(inverted[day][0].get("week_day"), day);
            });
        },

        "should invert dict with unordered slots": function () {

            var slots = {"1": [
                new Flod.TimeSlot({
                    "start_time": "14:00:00",
                    "end_time": "18:00:00",
                    "week_day": 1
                }),
                new Flod.TimeSlot({
                    "start_time": "10:00:00",
                    "end_time": "12:00:00",
                    "week_day": 1
                })
            ]};
            var inverted = Flod.calendar.invertSlots(slots);
            assert.equals(inverted["1"].length, 3);

            assert.equals(inverted["1"][0].get("start_time").format("HH:mm"), "08:00");
            assert.equals(inverted["1"][0].get("end_time").format("HH:mm"), "10:00");
            assert.equals(inverted["1"][0].get("week_day"), 1);

            assert.equals(inverted["1"][1].get("start_time").format("HH:mm"), "12:00");
            assert.equals(inverted["1"][1].get("end_time").format("HH:mm"), "14:00");
            assert.equals(inverted["1"][1].get("week_day"), 1);

            assert.equals(inverted["1"][2].get("start_time").format("HH:mm"), "18:00");
            assert.equals(inverted["1"][2].get("end_time").format("HH:mm"), "23:00");
            assert.equals(inverted["1"][2].get("week_day"), 1);

            _.each(_.range(2, 8), function (day) {
                assert.equals(inverted[day].length, 1);
                assert.equals(inverted[day][0].get("start_time").format("HH:mm"), "08:00");
                assert.equals(inverted[day][0].get("end_time").format("HH:mm"), "23:00");
                assert.equals(inverted[day][0].get("week_day"), day);
            });
        }
    });

    buster.testCase('util split test', {

        'should be able to split a full day slot with a start day slot': function () {
            var toSplit =  new Flod.TimeSlot({
                "start_time": "2014-06-04T08:00:00",
                "end_time": "2014-06-04T23:00:00"
            });

            var splitWith = [
                new Flod.TimeSlot({
                    "start_time": "2014-06-04T08:00:00",
                    "end_time": "2014-06-04T10:00:00"
                })
            ];

            var split = Flod.calendar.splitSlot(toSplit, splitWith);
            assert.equals(split.length, 1);
            assert.equals(split[0].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T10:00");
            assert.equals(split[0].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T23:00");
        },

        'should be able to split a full day slot with an end day slot': function () {
            var toSplit =  new Flod.TimeSlot({
                "start_time": "2014-06-04T08:00:00",
                "end_time": "2014-06-04T23:00:00"
            });

            var splitWith = [
                new Flod.TimeSlot({
                    "start_time": "2014-06-04T19:00:00",
                    "end_time": "2014-06-04T23:00:00"
                })
            ];

            var split = Flod.calendar.splitSlot(toSplit, splitWith);
            assert.equals(split.length, 1);
            assert.equals(split[0].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T08:00");
            assert.equals(split[0].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T19:00");
        },

        'should return no slots when equal': function () {
            var toSplit =  new Flod.TimeSlot({
                "start_time": "2014-06-04T08:00:00",
                "end_time": "2014-06-04T23:00:00"
            });

            var splitWith = [
                new Flod.TimeSlot({
                    "start_time": "2014-06-04T08:00:00",
                    "end_time": "2014-06-04T23:00:00"
                })
            ];

            var split = Flod.calendar.splitSlot(toSplit, splitWith);
            assert.equals(split.length, 0);
        },

        'should return two slots when in middle': function () {
            var toSplit =  new Flod.TimeSlot({
                "start_time": "2014-06-04T08:00:00",
                "end_time": "2014-06-04T23:00:00"
            });

            var splitWith = [
                new Flod.TimeSlot({
                    "start_time": "2014-06-04T10:00:00",
                    "end_time": "2014-06-04T12:00:00"
                })
            ];

            var split = Flod.calendar.splitSlot(toSplit, splitWith);
            assert.equals(split.length, 2);
            assert.equals(split[0].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T08:00");
            assert.equals(split[0].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T10:00");
            assert.equals(split[1].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T12:00");
            assert.equals(split[1].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T23:00");
        },

        'should handle overlap at start': function () {
            var toSplit =  new Flod.TimeSlot({
                "start_time": "2014-06-04T10:00:00",
                "end_time": "2014-06-04T23:00:00"
            });

            var splitWith = [
                new Flod.TimeSlot({
                    "start_time": "2014-06-04T9:00:00",
                    "end_time": "2014-06-04T12:00:00"
                })
            ];

            var split = Flod.calendar.splitSlot(toSplit, splitWith);
            assert.equals(split.length, 1);
            assert.equals(split[0].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T12:00");
            assert.equals(split[0].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T23:00");
        },

        'should handle overlap at end': function () {
            var toSplit =  new Flod.TimeSlot({
                "start_time": "2014-06-04T08:00:00",
                "end_time": "2014-06-04T20:00:00"
            });

            var splitWith = [
                new Flod.TimeSlot({
                    "start_time": "2014-06-04T18:00:00",
                    "end_time": "2014-06-04T23:00:00"
                })
            ];

            var split = Flod.calendar.splitSlot(toSplit, splitWith);
            assert.equals(split.length, 1);
            assert.equals(split[0].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T08:00");
            assert.equals(split[0].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T18:00");
        },

        'should handle no overlap': function () {
            var toSplit =  new Flod.TimeSlot({
                "start_time": "2014-06-04T08:00:00",
                "end_time": "2014-06-04T18:00:00"
            });

            var splitWith = [
                new Flod.TimeSlot({
                    "start_time": "2014-06-04T18:00:00",
                    "end_time": "2014-06-04T23:00:00"
                })
            ];

            var split = Flod.calendar.splitSlot(toSplit, splitWith);
            assert.equals(split.length, 1);
            assert.equals(split[0].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T08:00");
            assert.equals(split[0].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T18:00");
        },

        'should be able to split with two': function () {
            var toSplit =  new Flod.TimeSlot({
                "start_time": "2014-06-04T08:00:00",
                "end_time": "2014-06-04T23:00:00"
            });

            var splitWith = [
                new Flod.TimeSlot({
                    "start_time": "2014-06-04T09:00:00",
                    "end_time": "2014-06-04T12:00:00"
                }),
                new Flod.TimeSlot({
                    "start_time": "2014-06-04T13:00:00",
                    "end_time": "2014-06-04T22:00:00"
                })
            ];

            var split = Flod.calendar.splitSlot(toSplit, splitWith);
            assert.equals(split.length, 3);
            assert.equals(split[0].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T08:00");
            assert.equals(split[0].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T09:00");
            assert.equals(split[1].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T12:00");
            assert.equals(split[1].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T13:00");
            assert.equals(split[2].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T22:00");
            assert.equals(split[2].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T23:00");
        },

        'should be able to split with two unsorted': function () {
            var toSplit =  new Flod.TimeSlot({
                "start_time": "2014-06-04T08:00:00",
                "end_time": "2014-06-04T23:00:00"
            });

            var splitWith = [
                new Flod.TimeSlot({
                    "start_time": "2014-06-04T13:00:00",
                    "end_time": "2014-06-04T22:00:00"
                }),
                new Flod.TimeSlot({
                    "start_time": "2014-06-04T09:00:00",
                    "end_time": "2014-06-04T12:00:00"
                })
            ];

            var split = Flod.calendar.splitSlot(toSplit, splitWith);
            assert.equals(split.length, 3);
            assert.equals(split[0].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T08:00");
            assert.equals(split[0].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T09:00");
            assert.equals(split[1].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T12:00");
            assert.equals(split[1].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T13:00");
            assert.equals(split[2].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T22:00");
            assert.equals(split[2].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T23:00");
        },

        'should be able to split with tree unsorted': function () {
            var toSplit =  new Flod.TimeSlot({
                "start_time": "2014-06-04T09:00:00",
                "end_time": "2014-06-04T22:00:00"
            });

            var splitWith = [

                new Flod.TimeSlot({
                    "start_time": "2014-06-04T21:00:00",
                    "end_time": "2014-06-04T23:00:00"
                }),
                new Flod.TimeSlot({
                    "start_time": "2014-06-04T08:00:00",
                    "end_time": "2014-06-04T10:00:00"
                }),
                new Flod.TimeSlot({
                    "start_time": "2014-06-04T11:00:00",
                    "end_time": "2014-06-04T12:00:00"
                })
            ];

            var split = Flod.calendar.splitSlot(toSplit, splitWith);
            assert.equals(split.length, 2);
            assert.equals(split[0].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T10:00");
            assert.equals(split[0].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T11:00");
            assert.equals(split[1].get('start_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T12:00");
            assert.equals(split[1].get('end_time').format('YYYY-MM-DDTHH:mm'), "2014-06-04T21:00");

        }

    });

}(Flod));