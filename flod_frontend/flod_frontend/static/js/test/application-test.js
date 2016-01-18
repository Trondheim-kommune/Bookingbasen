(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('ApplicationTest', {

        "should serialize a singleApplication": function() {

            var application = new ns.SingleApplication({
                "text": "tekst",
                "organisation": {"uri": "/organisations/1"},
                "person": new Backbone.Model({"uri": "/person/1", "name": "Name"}),
                "resource": new Backbone.Model({"uri": "/facilities/1"}),
                "slots": []
            });

            var serialized = application.toJSON();
            assert.equals(serialized.text, "tekst");
            assert.equals(serialized.organisation.uri, "/organisations/1");
            assert.equals(serialized.person.uri, "/person/1");
            assert.equals(serialized.resource.uri, "/facilities/1");
        },

        "should serialize slots for a singleApplication": function () {

            var slots = [
                new ns.TimeSlot({
                    "start_time": "2013-09-04T14:30:00",
                    "end_time": "2013-09-04T15:30:00"
                }),
                new ns.TimeSlot({
                    "start_time": "2013-09-04T16:30:00",
                    "end_time": "2013-09-04T17:30:00"
                })
            ];

            var application = new ns.SingleApplication({
                "text": "tekst",
                "organisation": {"uri": "/organisations/1"},
                "person": new Backbone.Model({"uri": "/person/1", "name": "Name"}),
                "resource": new Backbone.Model({"uri": "/facilities/1"}),
                "slots": slots
            });

            var serialized = application.toJSON();
            var serialized_slots = serialized.slots;
            assert.equals(serialized_slots.length, 2);
            assert.equals(serialized_slots[0].start_time, "2013-09-04T14:30:00");
            assert.equals(serialized_slots[1].end_time, "2013-09-04T17:30:00");
            assert.equals(serialized.resource.uri, "/facilities/1");
        },

        "should serialize slots for a repeatingApplication": function () {

            var slots = [
                new ns.TimeSlot({
                    "start_time": "2013-09-04T14:30:00",
                    "end_time": "2013-09-04T15:30:00"
                }),
                new ns.TimeSlot({
                    "start_time": "2013-09-04T16:30:00",
                    "end_time": "2013-09-04T17:30:00"
                })
            ];

            var application = new ns.RepeatingApplication({
                "text": "tekst",
                "organisation": {"uri": "/organisations/1"},
                "person": new Backbone.Model({"uri": "/person/1", "name": "Name"}),
                "resource": new Backbone.Model({"uri": "/facilities/1"}),
                "slots": slots,
                "start_date": moment("2013-01-01T00:00:00"),
                "end_date": moment("2013-10-01T00:00:00")
            });

            var serialized = application.toJSON();
            var serialized_slots = serialized.slots;
            assert.equals(serialized_slots.length, 2);
            assert.equals(serialized_slots[0].get("start_time").format("HH:mm:ss"), "14:30:00");
            assert.equals(serialized_slots[0].get("end_time").format("HH:mm:ss"), "15:30:00");
            assert.equals(serialized_slots[0].get("start_time").format("YYYY-MM-DD"), "2013-09-04");
            assert.equals(serialized_slots[0].get("end_time").format("YYYY-MM-DD"), "2013-09-04");
            assert.equals(serialized.resource.get("uri"), "/facilities/1");
        }

    });
}(Flod));