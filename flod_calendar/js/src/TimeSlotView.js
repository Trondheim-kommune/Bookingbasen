var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    function checkResize(el, ui) {
        var parent = $($(el).parent().parent());
        var max = parent.position().left + parent.width() - 25;
        var width = ui.position.left + ui.size.width;
        if (width >= max) {
            $(el).resizable("option", {"maxWidth": ui.size.width});
        }
    }

    var SlotView = Backbone.View.extend({

        className: "timeslot",

        events: {
            "click": "clicked"
        },

        initialize: function () {
            this.model.on("change:display_name", this.render, this);
            _.bindAll(this, "clicked");
            this.model.on("change:selected", this.render, this);
            this.model.on("change:status", this.render, this);
        },

        render: function () {
            var colspan = (this.model.getDuration() / this.model.collection.options.slot_duration);
            this.$el.data("slot", this.model);
            if (this.model.hasChanged("status")) {
                this.$el.removeClass(this.model.previous("status").toLowerCase());
            }
            this.$el.addClass(this.model.getStatus());

            if (this.model.has("color")) {
                this.$el.css("background-color", this.model.get("color"));
            }

            this.$el.text(this.model.getLabel());
            this.$el.attr("title", this.model.getDisplayName());

            var width = (colspan * 26) + ((2 * colspan) - 1);
            this.$el.css("width", width + "px");

            if (this.model.get("editable")) {
                this.makeEditable();
            } else {
                if (this.$el.is('.ui-resizable')) {
                    this.$el.resizable("destroy");
                }
                if (this.$el.is('.ui-draggable')) {
                    this.$el.draggable("destroy");
                }
            }
            if (this.model.get("selected")) {
                this.$el.addClass("selected");
            } else {
                this.$el.removeClass("selected");
            }
            return this;
        },

        resized: function (event, ui) {
            var diff = ((ui.size.width - ui.originalSize.width) / 28) * 30;
            if (this.model.collection.canChangeSlotTo(this.model, moment(this.model.get("start_time")), moment(this.model.get("end_time")).add(diff, "minutes"))) {
                this.model.get("end_time").add(diff, "minutes");
            }
            this.model.trigger("slotChanged", this.model);
        },

        makeEditable: function () {

            var resized = _.bind(this.resized, this);

            var tbody;
            if (this.options.table) {
                tbody = this.options.table.$("tbody");
            }
            this.$el.draggable({
                grid: [28, 26],
                zIndex: 100,
                containment: tbody
            }).resizable({
                "grid": [28, 26],
                "handles": "e",
                start: function (event, ui) {
                    checkResize(this, ui);
                },
                stop: function (event, ui) {
                    $(this).resizable("option", {"maxWidth": null});
                    resized(event, ui);
                },
                resize: function (event, ui) {
                    checkResize(this, ui);
                    $(this).css('height', '');
                }
            });
        },

        clicked: function () {
            var coll = this.model.collection;
            if (_.has(this.model, "parentCollection")) {
                // Trigger click event on parent
                coll = this.model.parentCollection;
            }
            coll.trigger("slotClick", this.model);
        }

    });

    ns.TimeSlotView = Backbone.View.extend({

        className: "slot",

        tagName: "td",

        render: function () {
            var colspan = (this.model.getDuration() / this.options.slotDuration);
            this.slotView = new SlotView({"model": this.model, "table": this.options.table});
            this.$el.append(this.slotView.render(colspan).$el);
            this.$el.attr("colspan", colspan);
            return this;
        }
    });

}(Flod));
