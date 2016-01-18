var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    function isoWeeksInYear(year) {
        function weekOfYear(mom, firstDayOfWeek, firstDayOfWeekOfYear) {
            var end = firstDayOfWeekOfYear - firstDayOfWeek,
                daysToDayOfWeek = firstDayOfWeekOfYear - mom.day(),
                adjustedMoment;
            if (daysToDayOfWeek > end) {
                daysToDayOfWeek -= 7;
            }
            if (daysToDayOfWeek < end - 7) {
                daysToDayOfWeek += 7;
            }
            adjustedMoment = moment(mom).add(daysToDayOfWeek, 'd');
            return {
                week: Math.ceil(adjustedMoment.dayOfYear() / 7),
                year: adjustedMoment.year()
            };
        }

        function weeksInYear(year, dow, doy) {
            return weekOfYear(moment([year, 11, 31 + dow - doy]), dow, doy).week;
        }

        return weeksInYear(year, 1, 4);
    }


    ns.Week = Backbone.Model.extend({

        weekDayFormat: "dddd",
        dayFormat: "D.M",

        _getLastValidDay: function () {
            var firstDayOfYear = moment(this.get("year") + "-01-04", "YYYY-MM-DD"); // The Jan 4th must be in week 1 according to ISO
            firstDayOfYear.endOf("isoWeek");
            firstDayOfYear.add("w", parseInt(this.get("week"), 10) - 1);
            return firstDayOfYear;
        },

        _changeWeek: function (offset) {
            var numWeeks = isoWeeksInYear(this.get('year'));
            var current = this.get('week');
            var changedWeek = current + offset;

            var year = this.get('year');
            if (changedWeek < 1) {
                year = year - 1;
                changedWeek = isoWeeksInYear(year)+changedWeek;
            } else if (changedWeek > numWeeks) {
                year = year + 1;
                changedWeek = changedWeek - numWeeks;
            }
            this.set({
                "year": year,
                "week": changedWeek
            });
        },

        _asRange: function () {
            return moment().range(this.getFirstValidDay(), this._getLastValidDay());
        },

        getFirstValidDay: function () {
            var firstDayOfYear = moment(this.get("year") + "-01-04", "YYYY-MM-DD"); // The Jan 4th must be in week 1 according to ISO
            firstDayOfYear.startOf("isoWeek");
            firstDayOfYear.add("w", parseInt(this.get("week"), 10) - 1);
            return firstDayOfYear;
        },

        getDisplayStr: function () {
            return "Uke " + this.get("week") + ", " + this.get("year");
        },

        getDays: function () {
            var firstDay = this.getFirstValidDay();
            var lastDay = this._getLastValidDay();
            var diff = lastDay.diff(firstDay, "days");

            return _.map(_.range(0, diff + 1), function (offset) {
                var date = moment(firstDay).add("d", offset);
                return {
                    "moment": date
                };
            });
        },

        hasPrev: function () {
            if (!this.has("range")) {
                return true;
            }
            return !this._asRange().contains(this.get("range").start);

        },

        hasNext: function () {
            if (!this.has("range")) {
                return true;
            }
            return !this._asRange().contains(this.get("range").end);
        },

        next: function () {
            if (this.hasNext()) {
                this._changeWeek(1);
            }
            return this;
        },

        prev: function () {
            if (this.hasPrev()) {
                this._changeWeek(-1);
            }
            return this;
        },

        nextMonth: function () {
            if (this.hasNext()) {

                var nextWeek = this.get("week") + 4;

                if (this.has("range")) {
                    var rangeEnd = moment(this.get("range").end).isoWeek();
                    if (nextWeek > rangeEnd){
                        nextWeek = rangeEnd;
                    }
                }

                nextWeek -= this.get("week");

                this._changeWeek(nextWeek);
            }
            return this;
        },

        prevMonth: function () {
            if (this.hasPrev()) {
                var nextWeek = this.get("week") - 4;

                if (this.has("range")) {
                    var rangeEnd = moment(this.get("range").start).isoWeek();
                    if (nextWeek < rangeEnd){
                        nextWeek = rangeEnd;
                    }
                }

                nextWeek -= this.get("week");

                this._changeWeek(nextWeek);
            }
            return this;
        },

        equals: function (week) {
            return (this.get("week") === week.get("week") && this.get("year") === week.get("year"));
        }
    });

}(Flod));



