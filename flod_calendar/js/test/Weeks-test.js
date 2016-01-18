(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('WeekTest', {
        setUp: function () {

            this.currentWeek = new ns.Week({
                "year": 2013,
                "week": 24
            });

            this.weeks = new ns.Weeks({
                "week": this.currentWeek
            });
        },

        "should be defined": function () {
            assert(ns.Weeks);
        },

        "it should return corect display string": function () {
            assert.equals(this.weeks.getDisplayStr(), "Uke 24, 2013");
        },

        "it should get past, present and next week ": function () {
            var weeks = this.weeks.getWeeks();
            assert.equals(weeks.length, 3);
            assert.equals(weeks[0].get("week"), 23);
            assert.equals(weeks[1].get("week"), 24);
            assert.equals(weeks[2].get("week"), 25);

        },

        "it should always return true for hasnext and hasprev": function () {
            assert(this.weeks.hasNext());
            assert(this.weeks.hasPrev());
        }

    });
}(Flod));