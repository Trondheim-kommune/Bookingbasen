var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    moment.lang('no', {
        months : [
            "Januar", "Februar", "Mars", "April", "Mai", "Juni", "Juli",
            "August", "September", "Oktober", "November", "Desember"
        ],
        weekdays : [
            "Søndag", "Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag"
        ],
        weekdaysShort : ["S", "M", "T", "O", "T", "F", "L"]
    });

    moment.lang("no");


    var ElementView = Backbone.View.extend({

        tagName: "td",

        className: "selectable",

        events: {
            "click": "change"
        },

        initialize: function () {
            _.bindAll(this, "change");
        },

        render: function () {
            if (this.model.get("selected")) {
                this.$el.addClass("selected current");
            } else {
                this.$el.addClass("otherdate");
            }
            if (this.model.get("disabled")) {
                this.$el.addClass("disabled");
            }
        }
    });

    var DayView = ElementView.extend({


        template: "<div><%= day_name %></div><div><%= date %></div>",

        render: function () {
            ElementView.prototype.render.apply(this, arguments);
            this.$el.html(_.template(this.template, {
                "day_name": this.model.get("moment").format(this.model.get("weekDayFormat")),
                "date": this.model.get("moment").format(this.model.get("dayFormat"))
            }));
            return this;
        },

        change: function () {
            if (!this.model.get("disabled")) {
                this.options.parent.change(this.model.get("moment"));
            }
        }
    });


    var ChooserView = Backbone.View.extend({

        tagName: "table",

        className: "flod-calendar flod-calendar-chooser",

        template: '<tr><td><%= title %></td></tr>',

        render: function () {
            this.$el.html(_.template(this.template, {"title": this.model.getDisplayStr()}));
            if (this.model.hasPrev()) {
                var prevMonth = $('<td class="flod-btn"><i><img src="/static/images/backward2.png" height="26" width="17"></i></td>');
                this.$("tr").append(prevMonth);
                prevMonth.on("click", _.bind(this.prevMonth, this));

                var prevBtn = $('<td class="flod-btn"><i id="left"><img src="/static/images/backward1.png" height="26" width="17"></i></td>');
                this.$("tr").append(prevBtn);
                prevBtn.on("click", _.bind(this.prev, this));
            }

            this.renderElements();

            if (this.model.hasNext()){
                var nextBtn = $('<td class="flod-btn right"><i id="right"><img src="/static/images/forward1.png" height="26" width="17"></i></td>');
                this.$("tr").append(nextBtn);
                nextBtn.on("click", _.bind(this.next, this));

                var nextMonth = $('<td class="flod-btn"><i><img src="/static/images/forward2.png" height="26" width="17"></i></td>');
                this.$("tr").append(nextMonth);
                nextMonth.on("click", _.bind(this.nextMonth, this));
            }

            return this;
        },

        prev: function () {

        },

        prevMonth: function () {

        },

        next: function () {

        },

        nextMonth: function () {

        }
    });

    ns.WeekView = ChooserView.extend({

        renderElements: function () {
            var range;
            if (this.model.has("range")) {
                range = moment().range(moment(this.model.get("range").start.format("YYYY-MM-DD"), "YYYY-MM-DD"), moment(this.model.get("range").end.format("YYYY-MM-DD"), "YYYY-MM-DD"));
            }
            var days = _.map(this.model.getDays(), function (day) {
                day.weekDayFormat = this.model.weekDayFormat;
                day.dayFormat = this.model.dayFormat;
                if (this.options.selected) {
                    day.selected = this.options.selected.isSame(day.moment, "day");
                }
                if (range) {
                    day.disabled = !range.contains(day.moment);
                }
                return new DayView({"model": new Backbone.Model(day), "parent": this}).render().$el;
            }, this);
            this.$("tr").append(days);
        },

        change: function (day) {
            this.options.selected = day;
            this.trigger("changeDay", day);
            this.render();
        },

        prev: function () {
            if (this.model.hasPrev()) {
                this.model.prev();
                var d = moment(this.options.selected).subtract(7, "days").endOf("isoWeek");
                this.change(d);
            }
        },

        prevMonth: function () {
            if (this.model.hasPrev()) {
                this.model.prevMonth();
                var d = moment(this.options.selected).subtract(4, "w").endOf("isoWeek");
                if (this.model.has("range")) {
                    var rangeEnd = moment(this.model.get("range").start).endOf("isoWeek");
                    if (rangeEnd > d){
                        d = rangeEnd
                    }
                }
                this.change(d);
            }
        },

        next: function () {
            if (this.model.hasNext()) {
                this.model.next();
                var d = moment(this.options.selected).add(7, "days").startOf("isoWeek");
                this.change(d);
            }
        },

        nextMonth: function () {
            if (this.model.hasNext()) {
                this.model.nextMonth();
                var d = moment(this.options.selected).add(4, "w").startOf("isoWeek");
                if (this.model.has("range")) {
                    var rangeEnd = moment(this.model.get("range").end).startOf("isoWeek");
                    if (rangeEnd < d){
                        d = rangeEnd
                    }
                }
                this.change(d);
            }
        }
    });

    var WeekElementView = ElementView.extend({
        render: function () {
            ElementView.prototype.render.apply(this, arguments);
            this.$el.html("Uke " + this.model.get("week"));
            return this;
        },

        change: function () {
            this.options.parent.change(this.model);
        }
    });

    ns.WeeksView = ChooserView.extend({

        renderElements: function () {
            var weeks = _.map(this.model.getWeeks(), function (week) {
                week.set("selected", false);
                if (week.equals(this.model.get("week"))) {
                    week.set("selected", true);
                }
                return new WeekElementView({"model": week, "parent": this}).render().$el;
            }, this);
            this.$("tr").append(weeks);
        },

        change: function (week) {
            this.model.set("week", week);
            this.trigger("changeWeek", week);
            this.render();
        },

        prev: function () {
            this.change(this.model.prev());
        },

        next: function () {
            this.change(this.model.next());
        },

        prevMonth: function () {
            this.change(this.model.prevMonth());
        },

        nextMonth: function () {
            this.change(this.model.nextMonth());
        }
    });

}(Flod));