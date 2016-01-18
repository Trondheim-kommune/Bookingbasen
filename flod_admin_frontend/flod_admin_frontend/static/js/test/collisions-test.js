(function (ns) {
    "use strict";

    var assert = assert || buster.assertions.assert;
    var refute = refute || buster.assertions.refute;

    buster.testCase('CollisionTest', {

        setUp: function () {

            this.mappedSlots = {
                "2014-02-27": [
                    new ns.TimeSlot({"status": "Pending", "start_time": "2014-02-27T12:30:00", "display_name": "Privatperson", "uri": "/slots/25", "end_time": "2014-02-27T18:30:00"}),
                    new ns.TimeSlot({"status": "Pending", "start_time": "2014-02-27T08:00:00", "display_name": "Privatperson", "uri": "/requested_slots/32", "end_time": "2014-02-27T17:00:00"}),
                    new ns.TimeSlot({"status": "Granted", "start_time": "2014-02-27T08:00:00", "display_name": "Privatperson", "uri": "/slots/29", "end_time": "2014-02-27T10:00:00"}),
                    new ns.TimeSlot({"status": "Pending", "start_time": "2014-02-27T19:30:00", "display_name": "Privatperson", "uri": "/slots/34", "end_time": "2014-02-27T20:30:00"})
                ]
            };

        },

        "should find collisions given a dict sorted by date": function () {

            var slotsWithCollisions = ns.findCollisions(this.mappedSlots);

            assert.equals(slotsWithCollisions["2014-02-27"].length, 2);
        }

    });
}(Flod));