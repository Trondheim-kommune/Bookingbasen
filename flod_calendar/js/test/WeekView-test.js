(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('WeekViewTest', {

        setUp: function () {
            this.week = new ns.Week({
                "year": 2013,
                "week": 24
            });
        },

        "Should render correct title": function () {
            var weekView = new ns.WeekView({"model": this.week}).render();
            var first = $($(weekView.$("tbody").children()[0]).children()[0]);
            assert.equals(first.html(), "Uke 24, 2013");
        },

        "should render days": function () {
            var weekView = new ns.WeekView({"model": this.week}).render();
            var row = $(weekView.$("tbody").children()[0]);
            assert.equals(row.children().length, 12);

            var firstDay = $($(weekView.$("tbody").children()[0]).children()[3]);

            assert.equals($(firstDay.children()[0]).html(), "Mandag");
            assert.equals($(firstDay.children()[1]).html(), "10.6");
        },

        "should mark selected day as selected": function () {
            var weekView = new ns.WeekView({"model": this.week, "selected": moment("12.06.2013", "DD.MM.YYYY")}).render();
            var selectedDay = $($(weekView.$("tbody").children()[0]).children()[5]);
            assert(selectedDay.hasClass("selected"));
        },

        "should redraw and fire event on click on another day": function () {
            var weekView = new ns.WeekView({"model": this.week, "selected": moment("12.06.2013", "DD.MM.YYYY")}).render();
            var monday = $($(weekView.$("tbody").children()[0]).children()[3]);

            var spy = this.spy();
            weekView.on("changeDay", spy);
            monday.trigger("click");

            var mondayAfterRender = $($(weekView.$("tbody").children()[0]).children()[3]);
            assert(mondayAfterRender.hasClass("selected"));
            assert.calledOnce(spy);
            assert.equals(spy.args[0][0].format("dddd"), "Mandag");
        },

        "should go a week back on prev click": function () {
            var weekView = new ns.WeekView({"model": this.week, "selected": moment("10.06.2013", "DD.MM.YYYY")}).render();

            var spy = this.spy();
            weekView.on("changeDay", spy);

            var first = $($(weekView.$("tbody").children()[0]).children()[0]);
            assert.equals(first.html(), "Uke 24, 2013");

            var monday = $($(weekView.$("tbody").children()[0]).children()[3]);
            assert(monday.hasClass("selected"));

            var prevBtn = $($(weekView.$("tbody").children()[0]).children()[2]).find("i");
            prevBtn.trigger("click");
            var firstAgain = $($(weekView.$("tbody").children()[0]).children()[0]);
            assert.equals(firstAgain.html(), "Uke 23, 2013");

            var sundayAfterRender = $($(weekView.$("tbody").children()[0]).children()[9]);
            assert(sundayAfterRender.hasClass("selected"));
            assert.calledOnce(spy);
            assert.equals(spy.args[0][0].format("DD.MM.YYYY"), "09.06.2013");
        },


        "should go a week forward on next click": function () {
            var weekView = new ns.WeekView({"model": this.week, "selected": moment("11.06.2013", "DD.MM.YYYY")}).render();

            var spy = this.spy();
            weekView.on("changeDay", spy);

            var first = $($(weekView.$("tbody").children()[0]).children()[0]);
            assert.equals(first.html(), "Uke 24, 2013");

            var tuesday = $($(weekView.$("tbody").children()[0]).children()[4]);
            assert(tuesday.hasClass("selected"));

            var nextBtn = $($(weekView.$("tbody").children()[0]).children()[10]).find("i");
            nextBtn.trigger("click");
            var firstAgain = $($(weekView.$("tbody").children()[0]).children()[0]);
            assert.equals(firstAgain.html(), "Uke 25, 2013");

            var mondayAfterRender = $($(weekView.$("tbody").children()[0]).children()[3]);
            assert(mondayAfterRender.hasClass("selected"));
            assert.calledOnce(spy);
            assert.equals(spy.args[0][0].format("DD.MM.YYYY"), "17.06.2013");
        },

        "should go four weeks forward on next month click": function () {
            var range = {
                "start": moment("2013-06-10T00:00:00"),
                "end": moment("2013-06-10T23:00:00").add("days", 30)
            };
            this.week.set({"range": range});

            var weekView = new ns.WeekView({"model": this.week, "selected": moment("11.06.2013", "DD.MM.YYYY")}).render();

            var spy = this.spy();
            weekView.on("changeDay", spy);

            var first = $($(weekView.$("tbody").children()[0]).children()[0]);
            assert.equals(first.html(), "Uke 24, 2013");

            var tuesday = $($(weekView.$("tbody").children()[0]).children()[2]);
            assert(tuesday.hasClass("selected"));

            var nextBtn = $($(weekView.$("tbody").children()[0]).children()[9]).find("i");
            nextBtn.trigger("click");
            var firstAgain = $($(weekView.$("tbody").children()[0]).children()[0]);
            assert.equals(firstAgain.html(), "Uke 28, 2013");

            var mondayAfterRender = $($(weekView.$("tbody").children()[0]).children()[3]);
            assert(mondayAfterRender.hasClass("selected"));
            assert.calledOnce(spy);
            assert.equals(spy.args[0][0].format("DD.MM.YYYY"), "08.07.2013");
        },

        "should go four weeks back on previous month click": function () {
            var range = {
                "start": moment("2013-06-17T00:00:00").subtract("days", 30),
                "end": moment("2013-06-17T23:00:00")
            };
            this.week.set({"range": range});

            var weekView = new ns.WeekView({"model": this.week, "selected": moment("11.06.2013", "DD.MM.YYYY")}).render();

            var spy = this.spy();
            weekView.on("changeDay", spy);

            var first = $($(weekView.$("tbody").children()[0]).children()[0]);
            assert.equals(first.html(), "Uke 24, 2013");

            var tuesday = $($(weekView.$("tbody").children()[0]).children()[4]);
            assert(tuesday.hasClass("selected"));

            var nextBtn = $($(weekView.$("tbody").children()[0]).children()[1]).find("i");
            nextBtn.trigger("click");
            var firstAgain = $($(weekView.$("tbody").children()[0]).children()[0]);
            assert.equals(firstAgain.html(), "Uke 20, 2013");

            var mondayAfterRender = $($(weekView.$("tbody").children()[0]).children()[7]);
            assert(mondayAfterRender.hasClass("selected"));
            assert.calledOnce(spy);
            assert.equals(spy.args[0][0].format("DD.MM.YYYY"), "19.05.2013");
        },

        "should not go outside of end range on next month click": function () {
            var range = {
                "start": moment("2013-06-10T00:00:00"),
                "end": moment("2013-06-10T23:00:00").add("days", 13)
            };
            this.week.set({"range": range});

            var weekView = new ns.WeekView({"model": this.week, "selected": moment("11.06.2013", "DD.MM.YYYY")}).render();

            var spy = this.spy();
            weekView.on("changeDay", spy);

            var first = $($(weekView.$("tbody").children()[0]).children()[0]);
            assert.equals(first.html(), "Uke 24, 2013");

            var tuesday = $($(weekView.$("tbody").children()[0]).children()[2]);
            assert(tuesday.hasClass("selected"));

            var nextBtn = $($(weekView.$("tbody").children()[0]).children()[9]).find("i");
            nextBtn.trigger("click");
            var firstAgain = $($(weekView.$("tbody").children()[0]).children()[0]);
            assert.equals(firstAgain.html(), "Uke 25, 2013");

            var mondayAfterRender = $($(weekView.$("tbody").children()[0]).children()[3]);
            assert(mondayAfterRender.hasClass("selected"));
            assert.calledOnce(spy);
            assert.equals(spy.args[0][0].format("DD.MM.YYYY"), "17.06.2013");
        },

        "should not go outside of start range on previous month click": function () {
            var range = {
                "start": moment("2013-06-03T00:00:00"),
                "end": moment("2013-06-10T23:00:00").add("days", 13)
            };
            this.week.set({"range": range});

            var weekView = new ns.WeekView({"model": this.week, "selected": moment("11.06.2013", "DD.MM.YYYY")}).render();

            var spy = this.spy();
            weekView.on("changeDay", spy);

            var first = $($(weekView.$("tbody").children()[0]).children()[0]);
            assert.equals(first.html(), "Uke 24, 2013");

            var tuesday = $($(weekView.$("tbody").children()[0]).children()[4]);
            assert(tuesday.hasClass("selected"));

            var nextBtn = $($(weekView.$("tbody").children()[0]).children()[1]).find("i");
            nextBtn.trigger("click");
            var firstAgain = $($(weekView.$("tbody").children()[0]).children()[0]);
            assert.equals(firstAgain.html(), "Uke 23, 2013");

            var mondayAfterRender = $($(weekView.$("tbody").children()[0]).children()[7]);
            assert(mondayAfterRender.hasClass("selected"));
            assert.calledOnce(spy);
            assert.equals(spy.args[0][0].format("DD.MM.YYYY"), "09.06.2013");
        },

        "should not be able to go back if not inside range": function () {

            var range = {
                "start": moment("2013-06-10T00:00:00"),
                "end": moment("2013-06-10T00:00:00").add("days", 13)
            };
            this.week.set({"range": range});

            var weekView = new ns.WeekView({
                "model": this.week,
                "selected": moment("10.06.2013", "DD.MM.YYYY")
            }).render();

            refute(weekView.$("#left").length);
        },

        "should not be able to go forward if not inside range": function () {

            var range = {
                "start": moment("2013-06-10T00:00:00"),
                "end": moment("2013-06-10T00:00:00").add("days", 13)
            };
            this.week.set({"range": range});

            var weekView = new ns.WeekView({
                "model": this.week,
                "selected": moment("10.06.2013", "DD.MM.YYYY")
            }).render();

            assert(weekView.$("#right").length);

            weekView.$("#right").trigger("click");

            refute(weekView.$("#right").length);
        },

        "days after end of range should have disabled class and not trigger events": function () {
            var range = {
                "start": moment("2013-06-10T00:00:00"),
                "end": moment("2013-06-13T00:00:00")
            };
            this.week.set({"range": range});

            var weekView = new ns.WeekView({
                "model": this.week,
                "selected": moment("10.06.2013", "DD.MM.YYYY")
            }).render();

            var spy = this.spy();
            weekView.on("changeDay", spy);


            var friday = $($(weekView.$("tbody").children()[0]).children()[5]);

            assert(friday.hasClass("disabled"));
            friday.trigger("click");
            refute.called(spy);
        },

        "if same day but after should not add  disabledclass and not trigger events": function () {

            var range = {
                "start": moment("2013-06-10T23.59:00:00"),
                "end": moment("2013-06-10T00:00:00").add("days", 10)
            };

            var week = new Flod.Week({
                "year": 2013,
                "week": 24,
                "range": range
            });

            var weekView = new Flod.WeekView({"model": week, "selected": moment("12.06.2013", "DD.MM.YYYY")}).render();


            var monday = $($(weekView.$("tbody").children()[0]).children()[2]);

            refute(monday.hasClass("disabled"));
        }
    });
}(Flod));