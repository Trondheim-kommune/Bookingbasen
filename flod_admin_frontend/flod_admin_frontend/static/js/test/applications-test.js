(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;
    buster.testCase('//ApplicationCollecion Test', {

        setUp: function () {

            this.application1 = new ns.Application({
                "organisation": {"uri": "/organisations/1", "name": "Organisation 1", "num_members": 20},
                "resource": {"uri": "/facilities/1", "name": "name 1"},
                "person": {"uri": "/persons/1", "name": "Person 1"},
                "status": "Pending",
                "requested_repeating_slots": [
                    {
                        "start_time": "13:00:00",
                        "end_time": "15:00:00",
                        "start_date": "2013-09-07",
                        "end_date": "2013-09-07",
                        "resource": { "uri": "/resource/1" },
                        "week_day": 1
                    }
                ]
            });
            this.application2 = new ns.Application({
                "organisation": {"uri": "/organisations/2", "name": "Organisation 2", "num_members": 20},
                "resource": {"uri": "/facilities/1", "name": "name |"},
                "person": {"uri": "/persons/2", "name": "Person 2"},
                "status": "Pending",
                "requested_repeating_slots": [
                    {
                        "start_time": "10:00:00",
                        "end_time": "12:30:00",
                        "start_date": "2013-09-07",
                        "end_date": "2013-09-07",
                        "resource": { "uri": "/resource/1" },
                        "week_day": 2
                    }
                ]
            });

            this.application3 = new ns.Application({
                "organisation": {"uri": "/organisations/2", "name": "Organisation 2", "num_members": 20},
                "resource": {"uri": "/facilities/1", "name": "name 1"},
                "person": {"uri": "/persons/2", "name": "Person 2"},
                "status": "Pending",
                "requested_repeating_slots": [
                    {
                        "start_time": "13:00:00",
                        "end_time": "14:30:00",
                        "start_date": "2013-09-07",
                        "end_date": "2013-09-07",
                        "resource": { "uri": "/resource/1" },
                        "week_day": 1
                    }
                ]
            });

            this.application4 = new ns.Application({
                "organisation": {"uri": "/organisations/3", "name": "Organisation 3", "num_members": 20},
                "resource": {"uri": "/facilities/1", "name": "name 1"},
                "person": {"uri": "/persons/3", "name": "Person 3"},
                "status": "Pending",
                "requested_repeating_slots": [
                    {
                        "start_time": "14:00:00",
                        "end_time": "17:00:00",
                        "start_date": "2013-09-07",
                        "end_date": "2013-09-07",
                        "resource": { "uri": "/resource/1" },
                        "week_day": 1
                    }
                ]
            });

            this.application5 = new ns.Application({
                "organisation": {"uri": "/organisations/5", "name": "Organisation 5", "num_members": 20},
                "resource": {"uri": "/facilities/1", "name": "name 1"},
                "person": {"uri": "/persons/5", "name": "Person 5"},
                "status": "Pending",
                "requested_repeating_slots": [
                    {
                        "start_time": "13:00:00",
                        "end_time": "15:00:00",
                        "start_date": "2013-09-07",
                        "end_date": "2013-09-07",
                        "resource": { "uri": "/resource/1" },
                        "week_day": 2
                    }
                ]
            });

        },

        "should return all slots from all applications": function () {
            var applications = new ns.Applications([this.application1, this.application2]);
            var slots = applications.getSlots();
            assert.equals(slots.length, 2);
            assert(slots[0] instanceof ns.TimeSlot);
        },

        "should update slots with info from application": function () {
            var applications = new ns.Applications([this.application1, this.application2]);
            var slots = applications.getSlots();
            assert.equals(slots[0].get("status"), "Pending");
            assert.equals(slots[0].get("organisation").name, "Organisation 1");
            assert.equals(slots[0].get("person").name, "Person 1");
            assert.equals(slots[0].get("application"), this.application1.id);
        },

        "should return collisions as collision slots": function () {
            var applications = new ns.Applications([this.application1, this.application3]);
            var slots = applications.getSlots();
            assert.equals(slots.length, 1);
            assert(slots[0] instanceof ns.CollisionSlot);
        },

        "should return collisions as well as normal slots": function () {
            var applications = new ns.Applications([this.application1, this.application2, this.application3]);
            var slots = applications.getSlots();
            assert.equals(slots.length, 2);
            assert(slots[1] instanceof ns.CollisionSlot);
        },

        "collisionslot should have times combined form the slots its made up of": function () {
            var applications = new ns.Applications([this.application1, this.application3]);
            var collision = applications.getSlots()[0];
            assert.equals(collision.get("start_time").format("HH:mm"), "13:00");
            assert.equals(collision.get("end_time").format("HH:mm"), "15:00");
            assert.equals(collision.get("week_day"), 1);
        },

        "should detect three slots colliding": function () {
            var applications = new ns.Applications([this.application1, this.application3, this.application4]);
            var slots = applications.getSlots();
            assert.equals(slots.length, 1);
            assert(slots[0] instanceof ns.CollisionSlot);

            assert.equals(slots[0].get("start_time").format("HH:mm"), "13:00");
            assert.equals(slots[0].get("end_time").format("HH:mm"), "17:00");
        },

        "should not make collisions with different week days": function () {
            var applications = new ns.Applications([this.application1, this.application5]);
            var slots = applications.getSlots();
            assert.equals(slots.length, 2);
        },

        "should get correct slotType": function () {

            var requested_repeating_slots = new ns.Application({
                "status": "Pending",
                "requested_repeating_slots": [
                    {
                        "start_time": "13:00:00",
                        "end_time": "15:00:00",
                        "start_date": "2013-09-07",
                        "end_date": "2013-09-07",
                        "resource": { "uri": "/resource/1" },
                        "week_day": 1
                    }
                ]
            });

            var repeating_slots = new ns.Application({
                "status": "Processing",
                "repeating_slots": [
                    {
                        "start_time": "13:00:00",
                        "end_time": "15:00:00",
                        "start_date": "2013-09-07",
                        "end_date": "2013-09-07",
                        "resource": { "uri": "/resource/1" },
                        "week_day": 1
                    }
                ]
            });


            var requested_slots = new ns.Application({
                "status": "Pending",
                "requested_slots": [
                    {
                        "start_time": "2013-09-07T13:00:00",
                        "end_time": "2013-09-07T15:00:00",
                        "resource": { "uri": "/resource/1" }
                    }
                ]
            });

            var slots = new ns.Application({
                "status": "Processing",
                "slots": [
                    {
                        "start_time": "2013-09-07T13:00:00",
                        "end_time": "2013-09-07T15:00:00",
                        "resource": { "uri": "/resource/1" }
                    }
                ]
            });

            assert.equals(requested_repeating_slots.getSlotType(), "requested_repeating_slots");
            assert.equals(repeating_slots.getSlotType(), "repeating_slots");
            assert.equals(requested_slots.getSlotType(), "requested_slots");
            assert.equals(slots.getSlotType(), "slots");

            assert.equals(requested_repeating_slots.getType(), "repeating");
            assert.equals(repeating_slots.getType(), "repeating");
            assert.equals(requested_slots.getType(), "single");
            assert.equals(slots.getType(), "single");

        }

    });

}(Flod));