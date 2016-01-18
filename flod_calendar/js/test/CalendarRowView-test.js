(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('CalendarRowViewTest', {

        "Should render a row with empty slots": function () {

            var options = {
                "displayName": "myName",
                "slot_duration": 30,
                "calendar_start": moment("08:00", "HH:mm"),
                "calendar_end": moment("23:00", "HH:mm")
            };
            var row = new ns.CalendarRow([], options);

            var rowView = new ns.CalendarRowView({"collection": row}).render();

            assert.equals(rowView.$el.children().length, 31);
        },

        "Should render a row with one set slot": function () {

            var options = {
                "displayName": "myName",
                "slot_duration": 30,
                "calendar_start": moment("08:00", "HH:mm"),
                "calendar_end": moment("23:00", "HH:mm")
            };

            var slot = new Flod.TimeSlot({
                "start_time": "2013-10-05T08:30:00",
                "end_time": "2013-10-05T09:30:00"
            });

            var row = new ns.CalendarRow([slot], options);

            var rowView = new ns.CalendarRowView({"collection": row}).render();
            assert.equals(rowView.$el.children().length, 30);
            assert($(rowView.$el.children()[2]).find("div").hasClass("unknown"));
        },

        "should have display name in leftmost column": function () {

            var options = {
                "displayName": "myName",
                "slot_duration": 30,
                "calendar_start": moment("08:00", "HH:mm"),
                "calendar_end": moment("23:00", "HH:mm")
            };

            var row = new ns.CalendarRow([], options);

            var rowView = new ns.CalendarRowView({"collection": row}).render();
            assert.equals(rowView.$el.children().length, 31);
            assert($(rowView.$el.children()[0]).text(), "myName");
        },

        "should detect click on empty slot": function () {

            var options = {
                "displayName": "myName",
                "slot_duration": 30,
                "calendar_start": moment("08:00", "HH:mm"),
                "calendar_end": moment("23:00", "HH:mm")
            };

            var row = new ns.CalendarRow([], options);

            var rowView = new ns.CalendarRowView({"collection": row}).render();
            var first = $(rowView.$el.children()[1]);

            var spy = this.spy();
            row.on("emptySlotClick", spy);
            first.trigger("click");
            assert.calledOnce(spy);
            assert.equals(spy.args[0][0].start_time.format("HH:mm"), "08:00");
            assert.equals(spy.args[0][0].end_time.format("HH:mm"), "08:30");
        },

        "should show new slot when added to collection": function () {
            var options = {
                "displayName": "myName",
                "slot_duration": 30,
                "calendar_start": moment("08:00", "HH:mm"),
                "calendar_end": moment("23:00", "HH:mm")
            };

            var row = new ns.CalendarRow([], options);

            var rowView = new ns.CalendarRowView({"collection": row}).render();

            var first = $(rowView.$el.children()[1]);
            assert(first.hasClass("empty-slot"));

            var data = {
                "start_time": "2013-09-04T08:00:00",
                "end_time": "2013-09-04T08:30:00"
            };

            var ts = new Flod.TimeSlot(data);
            row.addSlot(ts);

            var second = $(rowView.$el.children()[1]);
            assert(second.find("div").hasClass("unknown"));
        },

        "should re-render when slot is removed from collection": function () {
            var options = {
                "displayName": "myName",
                "slot_duration": 30,
                "calendar_start": moment("08:00", "HH:mm"),
                "calendar_end": moment("23:00", "HH:mm")
            };

            var row = new ns.CalendarRow([], options);

            var rowView = new ns.CalendarRowView({"collection": row}).render();

            var first = $(rowView.$el.children()[1]);
            assert(first.hasClass("empty-slot"));

            var data = {
                "start_time": "2013-09-04T08:00:00",
                "end_time": "2013-09-04T08:30:00"
            };

            var ts = new Flod.TimeSlot(data);
            row.addSlot(ts);

            var second = $(rowView.$el.children()[1]);
            assert(second.find("div").hasClass("unknown"));
            ts.collection.remove(ts);

            var third = $(rowView.$el.children()[1]);
            assert(third.hasClass("empty-slot"));
        },

        "should make row droppable if editable is true": function () {

            var options = {
                "displayName": "myName",
                "slot_duration": 30,
                "calendar_start": moment("08:00", "HH:mm"),
                "calendar_end": moment("23:00", "HH:mm"),
                "editable": true
            };

            var row = new ns.CalendarRow([], options);
            var rowView = new ns.CalendarRowView({"collection": row}).render();
            assert(rowView.$el.hasClass("ui-droppable"));
        }

    });
}(Flod));