(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('CalendarViewTest', {

        setUp: function () {
            this.rows = [
                {"date": moment("2013-09-05"), "displayName": "Row1"},
                {"date": moment("2013-09-06"), "displayName": "Row2"},
                {"date": moment("2013-09-07"), "displayName": "Row3"}
            ];

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

            this.calendar = new ns.CalendarModel({
                "rows": this.rows,
                "title": "title",
                "subtitle": "subtitle"
            });

        },

        "Should render calendar": function () {
            var calendarView = new ns.CalendarView({"model": this.calendar}).render();
            assert.equals(calendarView.$("tbody").children().length, 3);
            assert.equals($(calendarView.$("tbody").children()[0]).children().length, 31);
        },

        "create its own calendar model if none given": function () {
            var calendarView = new ns.CalendarView();
            assert(calendarView.model);
        },

        "should have hours in header": function () {
            var calendarView = new ns.CalendarView({"model": this.calendar}).render();

            assert.equals(calendarView.$("thead").children().length, 2);
            var hoursRow = calendarView.$("thead").children()[0];
            assert.equals($(hoursRow).children().length, 16);

            var first = $($(calendarView.$("thead").children()[0]).children()[1]);
            assert.equals(first.html(), "8");
            assert.equals(parseInt(first.attr("colspan"), 10), 2);
            var last = $($(calendarView.$("thead").children()[0]).children()[15]);
            assert.equals(last.html(), "22");
        },

        "should have minutes in header": function () {
            var calendarView = new ns.CalendarView({"model": this.calendar}).render();
            assert.equals($(calendarView.$("thead").children()[1]).children().length, 31);
            var first = $($(calendarView.$("thead").children()[1]).children()[1]);
            assert.equals(first.html(), "00");
            var second = $($(calendarView.$("thead").children()[1]).children()[2]);
            assert.equals(second.html(), "30");

            assert($(calendarView.$("thead").children()[1]).hasClass("gray"));
        },

        "Should have title and subtitle": function () {
            var calendarView = new ns.CalendarView({"model": this.calendar}).render();
            var first = $($(calendarView.$("thead").children()[0]).children()[0]);
            assert.equals(first.html(), "title");
            var second = $($(calendarView.$("thead").children()[1]).children()[0]);
            assert.equals(second.html(), "subtitle");
        },

        "should detect click on empty slot": function () {
            var calendarView = new ns.CalendarView({"model": this.calendar}).render();
            var first = $($(calendarView.$("tbody").children()[0]).children()[1]);

            var spy = this.spy();
            calendarView.on("emptySlotClick", spy);
            first.trigger("click");

            assert.calledOnce(spy);
            assert.equals(spy.args[0][0].start_time.format("HH:mm"), "08:00");
            assert.equals(spy.args[0][0].end_time.format("HH:mm"), "08:30");
            assert.equals(spy.args[0][0].row.getDisplayName(), "Row1");
        },

        "should detect click on slot": function () {

            var rows = [
                {"date": moment("2013-09-05") ,"displayName": "Row1", slots: [{
                    "start_time": "2013-09-05T08:00:00",
                    "end_time": "2013-09-05T09:00:00"

                }]},
                {"date": moment("2013-09-06") ,"displayName": "Row2"},
                {"date": moment("2013-09-07") ,"displayName": "Row3"}
            ];

            var calendar = new ns.CalendarModel({
                "rows": rows,
                "title": "title",
                "subtitle": "subtitle"
            });

            var calendarView = new ns.CalendarView({"model": calendar}).render();
            var first = $($($(calendarView.$("tbody").children()[0]).children()[1]).children()[0]);

            var spy = this.spy();
            calendarView.on("slotClick", spy);
            first.trigger("click");

            assert.calledOnce(spy);

            assert.equals(spy.args[0][0].get("start_time").format("HH:mm"), "08:00");
            assert.equals(spy.args[0][0].get("end_time").format("HH:mm"), "09:00");
        },

        "Should re-render on set new rows": function () {
            var calendarView = new ns.CalendarView({"model": new ns.CalendarModel({})}).render();

            assert.equals(calendarView.$("tbody").children().length, 0);

            var data = [
                {
                    "start_time": "2013-09-05T14:30:00",
                    "end_time": "2013-09-05T16:30:00"
                }
            ];

            var row1 = new ns.CalendarRow(data, {"displayName": "row1", "date": moment("2013-09-05")});
            var row2 = new ns.CalendarRow(data, {"displayName": "row1", "date": moment("2013-09-05")});


            calendarView.model.reset([row1, row2]);
            assert.equals(calendarView.$("tbody").children().length, 2);
            assert.equals($(calendarView.$("tbody").children()[0]).children().find(".timeslot").length, 1);
        },

        "should get click events after reseting": function () {
            var calendarView = new ns.CalendarView({"model": new ns.CalendarModel({})}).render();
            var row1 = new ns.CalendarRow([], {"displayName": "row1", "date": moment("2013-09-05")});

            calendarView.model.reset([row1]);
            var spy = this.spy();
            calendarView.on("emptySlotClick", spy);
            var first = $($(calendarView.$("tbody").children()[0]).children()[1]);
            first.trigger("click");

            assert.calledOnce(spy);
        }

    });
}(Flod));