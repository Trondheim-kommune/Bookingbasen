(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('CalendarModelTest', {

        setUp: function () {
            this.rows = [
                {"date": moment("2013-09-05"), "displayName": "Row1"},
                {"date": moment("2013-09-06"), "displayName": "Row2"},
                {"date": moment("2013-09-07"), "displayName": "Row3"}
            ];
        },

        "should have a number of rows": function () {

            var calendar = new ns.CalendarModel({"rows": this.rows});
            assert.equals(calendar.get("rows").length, 3);

            assert(calendar.get("rows")[0] instanceof ns.CalendarRow);
        },

        "should have sensible defaults": function () {
            var calendar = new ns.CalendarModel();

            assert.equals(calendar.get("slot_duration"), 30);
            assert.equals(calendar.get("calendar_start").format("HH.mm"), "08.00");
            assert.equals(calendar.get("calendar_end").format("HH.mm"), "23.00");
        },

        "should add defaults to rows": function () {
            var calendar = new ns.CalendarModel({"rows": this.rows});
            assert.equals(calendar.row(0).options.slot_duration, 30);
            assert.equals(calendar.row(0).options.calendar_start.format("HH.mm"), "08.00");
            assert.equals(calendar.row(0).options.calendar_end.format("HH.mm"), "23.00");
        },

        "should be able to add slots": function () {

            this.rows[0].slots =  [
                {
                    "start_time": "2013-09-05T17:00:00",
                    "end_time": "2013-09-05T17:30:00"
                },
                {
                    "start_time": "2013-09-05T18:00:00",
                    "end_time": "2013-09-05T18:30:00"
                }
            ];

            this.rows[1].slots = [
                {
                    "start_time": "2013-09-06T17:00:00",
                    "end_time": "2013-09-06T17:30:00"
                },
                {
                    "start_time": "2013-09-06T18:00:00",
                    "end_time": "2013-09-06T18:30:00"
                }
            ];
            this.rows[2].slots = [
                {
                    "start_time": "2013-09-07T17:00:00",
                    "end_time": "2013-09-07T17:30:00"
                },
                {
                    "start_time": "2013-09-07T18:00:00",
                    "end_time": "2013-09-07T18:30:00"
                }
            ];

            var calendar = new ns.CalendarModel({"rows": this.rows});
            assert.equals(calendar.get("rows").length, 3);

            assert(calendar.get("rows")[0] instanceof ns.CalendarRow);
            assert.equals(calendar.get("rows")[0].length, 2);
            assert(calendar.get("rows")[0].at(0) instanceof ns.TimeSlot);
        },

        "should be able to get row by index": function () {
            var calendar = new ns.CalendarModel({"rows": this.rows});
            assert.equals(calendar.row(1).getDisplayName(), "Row2")
        },

        "should be able to remove all rows": function () {
            var calendar = new ns.CalendarModel({"rows": this.rows});
            assert.equals(calendar.get("rows").length, 3);
            calendar.reset();
            assert.equals(calendar.get("rows").length, 0);
        },

        "should be able to remove a given row": function () {
            var calendar = new ns.CalendarModel({"rows": this.rows});
            assert.equals(calendar.get("rows").length, 3);
            var row2 = calendar.row(1);
            row2.destroy();
            assert.equals(calendar.get("rows").length, 2);
        },

        "should be able to set new rows": function () {
            var calendar = new ns.CalendarModel({"rows": this.rows});
            assert.equals(calendar.get("rows").length, 3);
            assert.equals(calendar.row(0).getDisplayName(), "Row1");

            calendar.reset([{"displayName": "testrow"}]);
            assert.equals(calendar.get("rows").length, 1);
            assert.equals(calendar.row(0).getDisplayName(), "testrow");
        },

        "should be able to add new row": function () {
            var calendar = new ns.CalendarModel({"rows": this.rows});
            assert.equals(calendar.get("rows").length, 3);
            assert.equals(calendar.row(0).getDisplayName(), "Row1");

            calendar.addRow({"displayName": "testrow"});
            assert.equals(calendar.get("rows").length, 4);
            assert.equals(calendar.row(0).getDisplayName(), "Row1");
            assert.equals(calendar.row(3).getDisplayName(), "testrow");
        },

        "should be able to add new rows": function () {
            var calendar = new ns.CalendarModel({"rows": this.rows});
            assert.equals(calendar.get("rows").length, 3);
            assert.equals(calendar.row(0).getDisplayName(), "Row1");

            calendar.addRows([{"displayName": "testrow"}, {"displayName": "testrow 2"}]);
            assert.equals(calendar.get("rows").length, 5);
            assert.equals(calendar.row(0).getDisplayName(), "Row1");
            assert.equals(calendar.row(3).getDisplayName(), "testrow");
            assert.equals(calendar.row(4).getDisplayName(), "testrow 2");
        },

        "should be able to add new row as a RowModel": function () {
            var calendar = new ns.CalendarModel({"rows": this.rows});
            assert.equals(calendar.get("rows").length, 3);
            assert.equals(calendar.row(0).getDisplayName(), "Row1");
            var row = new ns.CalendarRow([], {"displayName": "testrow"});
            calendar.addRow(row);
            assert.equals(calendar.get("rows").length, 4);
            assert.equals(calendar.row(0).getDisplayName(), "Row1");
            assert.equals(calendar.row(3).getDisplayName(), "testrow");
        },

        "should be able to add new row at given index": function () {
            var calendar = new ns.CalendarModel({"rows": this.rows});
            assert.equals(calendar.get("rows").length, 3);
            assert.equals(calendar.row(0).getDisplayName(), "Row1");
            var row = new ns.CalendarRow([], {"displayName": "testrow"});
            calendar.addRow(row, 1);
            assert.equals(calendar.get("rows").length, 4);
            assert.equals(calendar.row(0).getDisplayName(), "Row1");
            assert.equals(calendar.row(1).getDisplayName(), "testrow");
        },

        "should be able to get index of row": function () {
            var calendar = new ns.CalendarModel({"rows": this.rows});
            var row = new ns.CalendarRow([], {"displayName": "testrow"});
            calendar.addRow(row, 1);
            assert.equals(calendar.get("rows").length, 4);

            assert.equals(calendar.getIndexForRow(row), 1);
        },

        "should be able to get all slots": function () {

            this.rows[0].slots =  [
                {
                    "start_time": "2013-09-05T17:00:00",
                    "end_time": "2013-09-05T17:30:00"
                },
                {
                    "start_time": "2013-09-05T18:00:00",
                    "end_time": "2013-09-05T18:30:00"
                }
            ];

            this.rows[1].slots = [
                {
                    "start_time": "2013-09-06T17:00:00",
                    "end_time": "2013-09-06T17:30:00"
                },
                {
                    "start_time": "2013-09-06T18:00:00",
                    "end_time": "2013-09-06T18:30:00"
                }
            ];
            this.rows[2].slots = [
                {
                    "start_time": "2013-09-07T17:00:00",
                    "end_time": "2013-09-07T17:30:00"
                },
                {
                    "start_time": "2013-09-07T18:00:00",
                    "end_time": "2013-09-07T18:30:00"
                }
            ];

            var calendar = new ns.CalendarModel({"rows": this.rows});

            var slots = calendar.getSlots();

            assert.equals(slots.length, 6);
            assert(slots[0] instanceof ns.TimeSlot);
        },

        "editable flag should be passed down to slots": function () {
            var options = {"date": moment("2013-09-05")};
            var row = new ns.CalendarRow([], options);
            var calendar = new ns.CalendarModel({
                "rows": [row],
                "title": "title",
                "subtitle": "subtitle",
                "editable": true
            });

            var slot = new Flod.TimeSlot({
                "start_time": "2013-10-05T14:00:00",
                "end_time": "2013-10-05T15:00:00"
            });
            refute(slot.get("editable"));
            calendar.row(0).addSlot(slot);
            assert(slot.get("editable"));
        },

        "editable flag should be passed down to slots when instanciated from json": function () {
            var rows = [{
                "date": moment("2013-09-05"),
                "displayName": "Row1",
                "slots":  [{
                    "start_time": "2013-09-05T15:00:00",
                    "end_time": "2013-09-05T16:00:00",
                    "organisation": {"uri": "/oranisations/1", "name": "Org 1 test"}
                }]
            }];

            var calendar = new Flod.CalendarModel({
                "rows": rows,
                "title": "title",
                "subtitle": "subtitle",
                "editable": true
            });
            var slots = calendar.getSlots();
            assert(slots[0].get("editable"));
        },

        "editable flag should default to false": function () {
            var options = {"date": moment("2013-09-05")};
            var row = new ns.CalendarRow([], options);
            var calendar = new ns.CalendarModel({
                "rows": [row],
                "title": "title",
                "subtitle": "subtitle"
            });

            var slot = new Flod.TimeSlot({
                "start_time": "2013-10-05T14:00:00",
                "end_time": "2013-10-05T15:00:00"
            });

            calendar.row(0).addSlot(slot);
            assert.equals(slot.get("editable"), false);
        },

        "slotChange event should bubble up to calendar": function () {

            var rows = [{
                "date": moment("2013-09-05"),
                "displayName": "Row1",
                "slots":  [{
                    "start_time": "2013-09-05T15:00:00",
                    "end_time": "2013-09-05T16:00:00",
                    "organisation": {"uri": "/oranisations/1", "name": "Org 1 test"}
                }]
            }];

            var calendar = new Flod.CalendarModel({
                "rows": rows,
                "title": "title",
                "subtitle": "subtitle",
                "editable": true
            });

            var spy = this.spy();
            calendar.on("slotChanged", spy);



            var slot = calendar.row(0).at(0);

            slot.get("start_time").add(30, "minutes");
            slot.get("end_time").add(30, "minutes");
            calendar.row(0).addSlot(slot);

            assert.calledOnce(spy);
        }

    });

}(Flod));