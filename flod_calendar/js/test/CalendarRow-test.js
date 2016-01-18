(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('CalendarRowTest', {

        setUp: function () {

            var data = [
                {
                    "start_time": "2013-09-05T14:30:00",
                    "end_time": "2013-09-05T16:30:00"
                },
                {
                    "start_time": "2013-09-05T17:30:00",
                    "end_time": "2013-09-05T20:30:00"
                }
            ];

            var options = {"date": moment("2013-09-05")};
            this.row = new ns.CalendarRow(data, options);
        },

        "should have displayName": function () {
            var options = {"displayName": "myName"};
            var row = new ns.CalendarRow([], options);
            assert.equals(row.getDisplayName(), options.displayName);
        },

        "should return empty string when no displayName": function () {
            var options = {};
            var row = new ns.CalendarRow([], options);
            assert.equals(row.getDisplayName(), "");
        },

        "should have a date set": function () {
            var options = {"date": "2013-09-05"};
            var row = new ns.CalendarRow([], options);
            assert(row.getDate().isSame(options.date));
        },

        "should handle date as moment": function () {
            var options = {"date": moment("2013-09-05")};
            var row = new ns.CalendarRow([], options);
            assert(row.getDate().isSame(options.date));
        },

        "should be able to initialize with slot data": function () {
            var data = [
                {
                    "start_time": "2013-09-05T14:30:00",
                    "end_time": "2013-09-05T16:30:00"
                },
                {
                    "start_time": "2013-09-05T17:30:00",
                    "end_time": "2013-09-05T20:30:00"
                }
            ];

            var options = {"date": moment("2013-09-05")};
            var row = new ns.CalendarRow(data, options);
            assert.equals(row.length, 2);
        },

        "should be able to add timeslot": function () {
            var options = {"date": moment("2013-09-05")};
            var row = new ns.CalendarRow([], options);

            var slot = new Flod.TimeSlot({
                "start_time": "2013-09-05T14:30:00",
                "end_time": "2013-09-05T16:30:00"
            });

            row.addSlot(slot);
            assert.equals(row.length, 1);
        },

        "added slot should have a reference to the row": function () {
            var options = {"date": moment("2013-09-05")};
            var row = new ns.CalendarRow([], options);

            var slot = new Flod.TimeSlot({
                "start_time": "2013-09-05T14:30:00",
                "end_time": "2013-09-05T16:30:00"
            });

            row.addSlot(slot);
            assert.equals(row.length, 1);
            assert.equals(slot.collection.cid, row.cid);
        },

        "initialized slot should have a reference to the row": function () {
            var options = {"date": moment("2013-09-05")};

            var slot = new Flod.TimeSlot({
                "start_time": "2013-09-05T14:30:00",
                "end_time": "2013-09-05T16:30:00"
            });
            var row = new ns.CalendarRow([slot], options);

            row.addSlot(slot);
            assert.equals(row.length, 1);
            assert.equals(slot.collection.cid, row.cid);
        },

        "should be able to add timeslots": function () {
            var options = {"date": moment("2013-09-05")};
            var row = new ns.CalendarRow([], options);

            var slot1 = new Flod.TimeSlot({
                "start_time": "2013-09-05T14:30:00",
                "end_time": "2013-09-05T16:30:00"
            });
            var slot2 = new Flod.TimeSlot({
                "start_time": "2013-09-05T17:30:00",
                "end_time": "2013-09-05T19:30:00"
            });

            row.addSlots([slot1, slot2]);
            assert.equals(row.length, 2);
        },

        "should be able to add timeslot with just time": function () {
            var options = {"date": moment("2013-09-05")};
            var row = new ns.CalendarRow([], options);

            var slot = new Flod.TimeSlot({
                "start_time": "14:30:00",
                "end_time": "16:30:00"
            });

            row.addSlot(slot);
            assert.equals(row.length, 1);
            assert.equals(row.at(0).get("start_time").format("YYYY-MM-DDTHH:mm:ss"), "2013-09-05T14:30:00");
            assert.equals(row.at(0).get("end_time").format("YYYY-MM-DDTHH:mm:ss"), "2013-09-05T16:30:00");
        },

        "add slot should change day": function () {
            var options = {"date": moment("2013-09-05")};
            var row = new ns.CalendarRow([], options);

            var slot = new Flod.TimeSlot({
                "start_time": "2013-09-01T14:30:00",
                "end_time": "2013-09-01T16:30:00"
            });

            row.addSlot(slot);
            assert.equals(row.at(0).get("start_time").format("YYYY-MM-DD"), "2013-09-05");
        },

        "should be able to add timeslot as object": function () {
            var options = {"date": moment("2013-09-05")};
            var row = new ns.CalendarRow([], options);

            var slot = {
                "start_time": "2013-09-05T14:30:00",
                "end_time": "2013-09-05T16:30:00"
            };

            row.addSlot(slot);
            assert.equals(row.length, 1);
        },

        "should detect collision on add": function () {
            var slot = new Flod.TimeSlot({
                "start_time": "2013-09-05T14:30:00",
                "end_time": "2013-09-05T16:30:00"
            });
            refute(this.row.addSlot(slot));
            assert.equals(this.row.length, 2);
        },

        "should add when no collision": function () {
            var slot = new Flod.TimeSlot({
                "start_time": "2013-09-05T08:30:00",
                "end_time": "2013-09-05T09:30:00"
            });
            assert(this.row.addSlot(slot));
            assert.equals(this.row.length, 3);
        },

        "should set correct date when no collision on add": function () {
            var slot = new Flod.TimeSlot({
                "start_time": "2013-10-05T08:30:00",
                "end_time": "2013-10-05T09:30:00"
            });
            assert(this.row.addSlot(slot));
            assert.equals(this.row.length, 3);
            assert.equals(this.row.at(2).get("start_time").format("YYYY-MM-DDTHH:mm:ss"), "2013-09-05T08:30:00");
            assert.equals(this.row.at(2).get("end_time").format("YYYY-MM-DDTHH:mm:ss"), "2013-09-05T09:30:00");
        },

        "should not change date when collision": function () {
            var slot = new Flod.TimeSlot({
                "start_time": "2013-10-05T14:00:00",
                "end_time": "2013-10-05T15:00:00"
            });
            refute(this.row.addSlot(slot));
            assert.equals(this.row.length, 2);
            assert.equals(slot.get("start_time").format("YYYY-MM-DDTHH:mm:ss"), "2013-10-05T14:00:00");
            assert.equals(slot.get("end_time").format("YYYY-MM-DDTHH:mm:ss"), "2013-10-05T15:00:00");
        },

        "should be able to move slots from one row to another": function () {
            var options = {"date": moment("2013-09-05")};
            var row2 = new ns.CalendarRow([], options);
            var slot = this.row.at(0);
            row2.addSlot(slot);
            assert.equals(this.row.length, 1);
            assert.equals(row2.length, 1);
        },

        "adding a slot to the row it is already in should trigger a change event": function () {
            var spy = this.spy();
            this.row.on("slotChanged", spy);

            var slot = this.row.at(0);

            slot.get("start_time").add(30, "minutes");
            slot.get("end_time").add(30, "minutes");
            this.row.addSlot(slot);

            assert.calledOnce(spy);
        },

        "removing a slot to the row it is in should trigger an event": function () {
            var spy = this.spy();
            this.row.on("remove", spy);

            var options = {"date": moment("2013-09-05")};
            var row2 = new ns.CalendarRow([], options);
            var slot = this.row.at(0);
            row2.addSlot(slot);
            assert.equals(this.row.length, 1);
            assert.equals(row2.length, 1);
            assert.calledOnce(spy);
        },

        "should not be able to move slots from one row to another if flag onlyOwn set": function () {
            var options = {"date": moment("2013-09-05")};
            var row2 = new ns.CalendarRow([], options);
            row2.onlyOwn = true;
            var slot = this.row.at(0);
            refute(row2.canChangeSlotTo(slot));
        },

        "should be able to move a slot on the row it is in with onlyOwn set": function () {
            this.row.onlyOwn = true;
            var slot = this.row.at(0);

            assert(this.row.canChangeSlotTo(
                slot,
                moment(slot.get("start_time")).add(30, "minutes"),
                moment(slot.get("end_time")).add(30, "minutes")
            ));
        },

        "should be able to check if a slot can have start and end time changed": function () {
            var data = [
                {
                    "start_time": "2013-09-05T14:30:00",
                    "end_time": "2013-09-05T16:30:00"
                },
                {
                    "start_time": "2013-09-05T17:30:00",
                    "end_time": "2013-09-05T20:30:00"
                }
            ];

            var options = {"date": moment("2013-09-05")};
            var row = new ns.CalendarRow(data, options);
            var slot = row.at(0);

            assert(row.canChangeSlotTo(slot, moment("20:30", "HH:mm"), moment("21:00", "HH:mm")));
            refute(row.canChangeSlotTo(slot, moment("17:00", "HH:mm"), moment("21:00", "HH:mm")));
            assert(row.canChangeSlotTo(slot, moment("14:30", "HH:mm"), moment("16:00", "HH:mm")));
            refute(row.canChangeSlotTo(slot, moment("14:30", "HH:mm"), moment("20:00", "HH:mm")));
        },

        "should be able get slot that starts at given time": function () {
            var slot = this.row.getByStart(moment("14:30", "HH:mm"));
            assert(slot);
            assert.equals(slot.get("start_time").format("HH.mm"), "14.30");
        },

        "should be to determine if a slot covers time": function () {
            assert(this.row.timeOccupied(moment("15:00", "HH:mm")));
            refute(this.row.timeOccupied(moment("14:30", "HH:mm")));
            refute(this.row.timeOccupied(moment("16:30", "HH:mm")));
            refute(this.row.timeOccupied(moment("22:00", "HH:mm")));
        },

        "editable flag should be passed down to slots": function () {
            var options = {"date": moment("2013-09-05"), "editable": true};
            var row2 = new ns.CalendarRow([], options);
            var slot = new Flod.TimeSlot({
                "start_time": "2013-10-05T14:00:00",
                "end_time": "2013-10-05T15:00:00"
            });
            refute(slot.get("editable"));
            row2.addSlot(slot);
            assert(slot.get("editable"));
        },

        "editable should not be overwritten if set to false": function () {
            var options = {"date": moment("2013-09-05"), "editable": true};
            var row2 = new ns.CalendarRow([], options);
            var slot = new Flod.TimeSlot({
                "start_time": "2013-10-05T14:00:00",
                "end_time": "2013-10-05T15:00:00",
                "editable": false
            });
            refute(slot.get("editable"));
            row2.addSlot(slot);
            refute(slot.get("editable"));
        },

        "editable should be overwritten if set to true": function () {
            var options = {"date": moment("2013-09-05"), "editable": false};
            var row2 = new ns.CalendarRow([], options);
            var slot = new Flod.TimeSlot({
                "start_time": "2013-10-05T14:00:00",
                "end_time": "2013-10-05T15:00:00",
                "editable": true
            });
            assert(slot.get("editable"));
            row2.addSlot(slot);
            refute(slot.get("editable"));
        },

        "should be able to get available time span": function () {
            var span = this.row.getAvailableSpan(moment("2013-09-05T16:30:00"));
            assert.equals(span.format(), moment("2013-09-05T17:30:00").format());
        },

        "should get last possible when no slots after": function () {
            var options = {
                "date": moment("2013-09-05"),
                "editable": false,
                "calendar_start": moment("08:00", "HH:mm"),
                "calendar_end": moment("23:00", "HH:mm")
            };
            var row2 = new ns.CalendarRow([], options);
            var span = row2.getAvailableSpan(moment("2013-09-05T16:30:00"));
            assert.equals(span.format(), moment("2013-09-05T23:00:00").format());
        }

    });

}(Flod));