var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";


    var EmptySlotView = ns.TimeSlotView.extend({

        events: {
            "click": "clicked"
        },

        className: "slot empty-slot",

        initialize: function () {
            _.bindAll(this, "clicked");
        },

        render: function () {
            this.$el.css('background-color', this.options.background_color);
            return this;
        },

        clicked: function () {
            this.collection.trigger("emptySlotClick", {
                "start_time": this.options.start_time,
                "end_time": this.options.end_time,
                "row": this.collection
            });
        }
    });

    ns.CalendarRowView = Backbone.View.extend({

        tagName: "tr",

        className: "calendar-row",

        initialize: function () {
            _.bindAll(this, "slotDropped");
            this.collection.on("add", this.render, this);
            this.collection.on("remove", this.render, this);
            this.collection.on("slotChanged", this.render, this);
            this.collection.on("slotRemoved", this.render, this);
            this.collection.on("slotRemoved", this.slotRemoved, this);
            this.collection.colors.on("add", this.render, this);
            this.collection.colors.on("remove", this.render, this);
        },

        render: function () {
            this.$el.html($("<td><div class='slot_title' title='" + this.collection.getDisplayName() + "'>" + this.collection.getDisplayName() + "</div></td>"));
            var start = this.collection.options.calendar_start;
            var duration = this.collection.options.slot_duration;
            this.views = _.compact(_.times(this.getNumSlots(), function (index) {
                var slot_start = moment(start).add("minutes", index * duration);
                var slot_end = moment(start).add("minutes", (index + 1) * duration);
                var slot = this.collection.getByStart(slot_start);
                if (slot) {
                    return new ns.TimeSlotView({
                        "model": slot,
                        "slotDuration": duration,
                        "table": this.options.table
                    }).render();
                } else if (!this.collection.timeOccupied(slot_start)) {
                    // Default color is white.
                    var background_color = "#FFFFFF";
                    var colorModel = this.collection.colors.getByTime(slot_start);
                    if (colorModel) {
                        background_color = colorModel.get("background_color");
                    }
                    return new EmptySlotView({
                        "collection": this.collection,
                        "slotDuration": duration,
                        "start_time": slot_start,
                        "end_time": slot_end,
                        "background_color": background_color
                    }).render();
                }
                return null;
            }, this));

            this.$el.append(_.pluck(this.views, "$el"));

            if (this.collection.options.editable) {
                this.$el.droppable({
                    drop: _.bind(function (event, ui) {
                        var offset = (ui.position.left / 28) * 30;
                        var new_start = moment(ui.draggable.data("slot").get("start_time").format("HH:mm"), "HH:mm").add("m", offset);
                        this.slotDropped(ui.draggable.data("slot"), new_start);
                    }, this)
                });
            }
            return this;
        },

        slotDropped: function (slot, time) {

            var diff = time.diff(moment(slot.get("start_time").format("HH:mm"), "HH:mm"), "minutes");

            if (this.collection.canChangeSlotTo(slot, moment(slot.get("start_time")).add(diff, "minutes"), moment(slot.get("end_time")).add(diff, "minutes"))) {
                slot.get("start_time").add(diff, "minutes");
                slot.get("end_time").add(diff, "minutes");
                this.collection.addSlot(slot);
            } else {
                slot.collection.trigger("slotChanged", slot);
            }
        },

        getNumSlots: function () {
            var opts = this.collection.options;
            return opts.calendar_end.diff(opts.calendar_start, "hours") * 60 / opts.slot_duration;
        },

        slotRemoved: function() {
            this.trigger("slotRemoved", this);
        }
    });

}(Flod));