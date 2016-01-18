(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('WeeksViewTest', {

        setUp: function () {

            this.currentWeek = new ns.Week({
                "year": 2013,
                "week": 24
            });

            this.weeks = new ns.Weeks({
                "week": this.currentWeek
            });
        },

        "should render correct title": function () {
            var weeksView = new ns.WeeksView({"model": this.weeks}).render();
            var first = $($(weeksView.$("tbody").children()[0]).children()[0]);
            assert.equals(first.html(), "Uke 24, 2013");
        },

        "should render weeks": function () {
            var weeksView = new ns.WeeksView({"model": this.weeks}).render();
            var row = $(weeksView.$("tbody").children()[0]);
            assert.equals(row.children().length, 8);

            var firstWeek = $($(weeksView.$("tbody").children()[0]).children()[3]);
            assert.equals(firstWeek.html(), "Uke 23");
        },

        "should mark selected week as selected": function () {
            var weeksView = new ns.WeeksView({"model": this.weeks}).render();
            var selectedWeek = $($(weeksView.$("tbody").children()[0]).children()[4]);
            assert(selectedWeek.hasClass("selected"));
        },

        "should redraw and fire event on click on another week": function () {
            var weeksView = new ns.WeeksView({"model": this.weeks}).render();
            var week23 = $($(weeksView.$("tbody").children()[0]).children()[3]);

            var spy = this.spy();
            weeksView.on("changeWeek", spy);
            week23.trigger("click");

            var week23AfterRender = $($(weeksView.$("tbody").children()[0]).children()[4]);
            assert(week23AfterRender.hasClass("selected"));
            assert.equals(week23AfterRender.html(), "Uke 23");
            assert.calledOnce(spy);
            var week = spy.args[0][0];
            assert.equals(week.get("week"), 23);
            assert.equals(week.get("year"), 2013);
        },

        "should go a week back on prev click": function () {
            var weeksView = new ns.WeeksView({"model": this.weeks}).render();

            var spy = this.spy();
            weeksView.on("changeWeek", spy);

            var first = $($(weeksView.$("tbody").children()[0]).children()[0]);
            assert.equals(first.html(), "Uke 24, 2013");

            var prevBtn = $($(weeksView.$("tbody").children()[0]).children()[2]).find("i");
            prevBtn.trigger("click");
            var firstAgain = $($(weeksView.$("tbody").children()[0]).children()[0]);
            assert.equals(firstAgain.html(), "Uke 23, 2013");

            assert.calledOnce(spy);
            var week = spy.args[0][0];
            assert.equals(week.get("week"), 23);
            assert.equals(week.get("year"), 2013);
        },

        "should go four weeks back on prev month click": function () {
            var weeksView = new ns.WeeksView({"model": this.weeks}).render();

            var spy = this.spy();
            weeksView.on("changeWeek", spy);

            var first = $($(weeksView.$("tbody").children()[0]).children()[0]);
            assert.equals(first.html(), "Uke 24, 2013");

            var prevBtn = $($(weeksView.$("tbody").children()[0]).children()[1]).find("i");
            prevBtn.trigger("click");
            var firstAgain = $($(weeksView.$("tbody").children()[0]).children()[0]);
            assert.equals(firstAgain.html(), "Uke 20, 2013");

            assert.calledOnce(spy);
            var week = spy.args[0][0];
            assert.equals(week.get("week"), 20);
            assert.equals(week.get("year"), 2013);
        },

        "should go a week forward on next click": function () {
            var weeksView = new ns.WeeksView({"model": this.weeks}).render();

            var spy = this.spy();
            weeksView.on("changeWeek", spy);

            var first = $($(weeksView.$("tbody").children()[0]).children()[0]);
            assert.equals(first.html(), "Uke 24, 2013");

            var nextBtn = $($(weeksView.$("tbody").children()[0]).children()[6]).find("i");
            nextBtn.trigger("click");
            var firstAgain = $($(weeksView.$("tbody").children()[0]).children()[0]);
            assert.equals(firstAgain.html(), "Uke 25, 2013");

            assert.calledOnce(spy);
            var week = spy.args[0][0];
            assert.equals(week.get("week"), 25);
            assert.equals(week.get("year"), 2013);
        },

        "should go four weeks forward on next month": function () {
            var weeksView = new ns.WeeksView({"model": this.weeks}).render();

            var spy = this.spy();
            weeksView.on("changeWeek", spy);

            var first = $($(weeksView.$("tbody").children()[0]).children()[0]);
            assert.equals(first.html(), "Uke 24, 2013");

            var nextBtn = $($(weeksView.$("tbody").children()[0]).children()[7]).find("i");
            nextBtn.trigger("click");
            var firstAgain = $($(weeksView.$("tbody").children()[0]).children()[0]);
            assert.equals(firstAgain.html(), "Uke 28, 2013");

            assert.calledOnce(spy);
            var week = spy.args[0][0];
            assert.equals(week.get("week"), 28);
            assert.equals(week.get("year"), 2013);
        }


    });
}(Flod));