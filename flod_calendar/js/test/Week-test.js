(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('WeekTest', {

        setUp: function () {
            this.week = new ns.Week({
                "year": 2013,
                "week": 24
            });
        },

        "Week should be defined": function () {
            assert(ns.Week);
        },

        "it should find the right display string": function () {
            assert.equals(this.week.getDisplayStr(), "Uke 24, 2013");
        },

        "it should get all days": function () {
            var days = this.week.getDays();
            assert.equals(days.length, 7);
            assert.equals(days[0].moment.format("YYYY-MM-DD"), "2013-06-10");
            assert.equals(days[6].moment.format("YYYY-MM-DD"), "2013-06-16");
        },

        "it should go to next week": function () {
            var next = this.week.next();
            assert.equals(next.getDisplayStr(), "Uke 25, 2013");
        },

        "it should go to next week and change year": function () {
            var week = new ns.Week({
                "year": 2012,
                "week": 52
            });
            var next = week.next();
            assert.equals(next.getDisplayStr(), "Uke 1, 2013");
        },

        "it should go to prev week": function () {
            var prev = this.week.prev();
            assert.equals(prev.getDisplayStr(), "Uke 23, 2013");
        },

        "it should go to prev week across year": function () {
            var week = new ns.Week({
                "year": 2013,
                "week": 1
            });
            var prev = week.prev();
            assert.equals(prev.getDisplayStr(), "Uke 52, 2012");
        },

        "it should go to prev week near new years": function () {
            var week = new ns.Week({
                "year": 2013,
                "week": 2
            });
            var prev = week.prev();
            assert.equals(prev.getDisplayStr(), "Uke 1, 2013");
        },

        "it should get first day of new period as moment": function () {
            var next = this.week.next();
            var day = next.getFirstValidDay();
            assert.equals(day.format("YYYY-MM-DDTHH:mm:ss"), "2013-06-17T00:00:00");
        },


        "it should be limited by range if set": function () {
            var range = {
                "start": moment("2013-06-10T00:00:00"),
                "end": moment("2013-06-40T00:00:00").add("days", 20)
            };
            this.week.set({"range": range});
            assert.equals(this.week.hasPrev(), false);
            assert.equals(this.week.hasNext(), true);
            this.week.prev();
            assert.equals(this.week.getDisplayStr(), "Uke 24, 2013");
        },

        "it should be able to compare to another week": function () {

            assert(
                this.week.equals(
                    new ns.Week({
                        "year": 2013,
                        "week": 24
                    }
                        )
                )
            );

            refute(
                this.week.equals(
                    new ns.Week({
                        "year": 2013,
                        "week": 23
                    }
                        )
                )
            );

            refute(
                this.week.equals(
                    new ns.Week({
                        "year": 2012,
                        "week": 24
                    }
                        )
                )
            );
        }
    });
}(Flod));