var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    function getNumSlots(start, end, duration) {
        return end.diff(start, "hours") * 60 / duration;
    }

    function addToTr(title, elements, className) {
        var tr = $("<tr><th class='first'>" + title + "</th></tr>");
        tr.append(elements);
        if (className) {
            tr.addClass(className);
        }
        return tr;
    }

    var CalendarHeader = Backbone.View.extend({

        tagName: "thead",

        render: function () {
            var numSlots = getNumSlots(
                this.model.get("calendar_start"),
                this.model.get("calendar_end"),
                this.model.get("slot_duration")
            );
            var start = this.model.get("calendar_start");
            var duration = this.model.get("slot_duration");

            var hours = _.compact(_.times(numSlots, function (index) {
                var slot_start = moment(start).add("minutes", index * duration);
                if (slot_start.minutes() === 0) {
                    return $("<th colspan='2'>" + slot_start.format("H") + "</th>");
                }
            }));
            var minutes = _.compact(_.times(numSlots, function (index) {
                var slot_start = moment(start).add("minutes", index * duration);
                return $("<th>" + slot_start.format("mm") + "</th>");
            }));

            this.$el.append(addToTr(this.model.get("title"), hours));
            this.$el.append(addToTr(this.model.get("subtitle"), minutes, "gray"));

            return this;
        }

    });

    ns.CalendarView = Backbone.View.extend({

        tagName: "table",

        className: "flod-calendar",

        initialize: function () {
            if (!this.model) {
                this.model = new ns.CalendarModel();
            }
            this.model.on("emptySlotClick", this.emptySlotClick, this);
            this.model.on("slotClick", this.slotClick, this);
            this.model.on("reset", this.render, this);
        },

        emptySlotClick: function (e) {
            this.trigger("emptySlotClick", e);
        },

        slotClick: function (e) {
            this.trigger("slotClick", e);
        },

        render: function () {

            if (this.views) {
                _.each(this.views, function (view) {
                    view.undelegateEvents();
                });
            }

            this.header = new CalendarHeader({"model": this.model}).render();

            this.$el.html(this.header.$el);
            this.$el.append($("<tbody></tbody>"));
            this.views = _.map(this.model.get("rows"), function (row) {
                var v = new ns.CalendarRowView({collection: row, "table": this});
                v.on("slotRemoved", this.slotRemoved, this);
                return v.render();
            }, this);
            this.$el.append(_.pluck(this.views, "$el"));
            return this;
        },

        getNumSlots: function () {
            return this.model.get("calendar_end").diff(this.model.get("calendar_start"), "hours") * 60 / this.model.get("slot_duration");
        },

        slotRemoved: function() {
            this.trigger("slotRemoved", this);
        }
    });

}(Flod));