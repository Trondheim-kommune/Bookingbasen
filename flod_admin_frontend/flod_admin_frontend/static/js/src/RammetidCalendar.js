var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.RammetidCalendar = ns.IdealizedWeeklyCalendarView.extend({
        initialize: function () {
            ns.IdealizedWeeklyCalendarView.prototype.initialize.apply(this, arguments);
            this.calendar.on("slotClick", this.slotClicked, this);
            this.on("emptySlotClick", this.emptySlotClick, this);
            this.shown = false;
        },
        render: function () {
            ns.IdealizedWeeklyCalendarView.prototype.render.apply(this, arguments);
            return this;
        },
        resetRows: function () {
            this.calendarView.model.reset(
                _.map(this.getDays(this.getInitDate()), function (day) {
                    return {"displayName": day.moment.format("dddd"), "date": day.moment};
                })
            );
            var blocked = new ns.WeeklyBlockedSlots([], {
                resource_uri: this.data.resource.get("uri"),
                start_date: moment(this.data.dates.start_date).format("YYYY-MM-DD"),
                end_date: moment(this.data.dates.end_date).format("YYYY-MM-DD")
            });
            var rammetidSlots = new ns.RammetidSlots([], {
                resource_uri: this.data.resource.get("uri"),
                start_date: moment(this.data.dates.start_date).format("YYYY-MM-DD"),
                end_date: moment(this.data.dates.end_date).format("YYYY-MM-DD")
            });
            // Wait before both rammetid and blocked slots
            // are fetched before calling slotsFetched function
            var showSlots = _.after(2, _.bind(function () {
                this.slotsFectched(rammetidSlots, blocked);
            }, this));
            rammetidSlots.fetch({"success": showSlots});
            blocked.fetch({"success": showSlots});
        },
        slotsFectched: function (rammetidSlots, blocked) {
            rammetidSlots.each(function (rammetidSlot) {
                rammetidSlot.set({
                    display_name: '',
                    editable: false,
                    status: 'other'
                });
                var umbrellaOrganisationUri = rammetidSlot.get("umbrella_organisation").uri;
                var umbrellaOrganisation = this.options.umbrellaOrganisations.getByUri(umbrellaOrganisationUri);
                if (umbrellaOrganisation) {
                    rammetidSlot.set({
                        display_name: umbrellaOrganisation.get("name"),
                        color: umbrellaOrganisation.get('color')
                    });
                }
            }, this);
            var mappedSlots = rammetidSlots.reduce(ns.mapSlotsByWeekday, {});
            var mappedBlocked = blocked.reduce(ns.mapSlotsByWeekday, {});
            mappedSlots = ns.findCollisions(ns.concatSlots(mappedSlots, mappedBlocked));
            mappedSlots = ns.findOverlapping(mappedSlots);
            _.each(mappedSlots, function (slots, weekday) {
                var row = this.calendar.getRowForWeekday(weekday);
                row.addSlots(slots);
            }, this);
        },
        show: function (data) {
            this.data = data;
            this.render();
            this.shown = true;
        },
        hide: function () {
            this.$el.html("");
            this.shown = false;
        },
        emptySlotClick: function (data) {
            var row = data.row;
            if (row.options && row.options.conflict === true) {
                return;
            }

            //check to see if this slot can be merged with other new ones
            var other = row.filter(function (slot) {
                return (slot.get('status') === 'Unknown') && ns.isNextTo(data, slot);
            });
            if (other.length) {
                data = ns.extendData(data, other);
                _.each(other, function (slot) {
                    row.removeSlot(slot);
                });
            }
            row.addSlot(new Flod.TimeSlot(data));
            this.trigger("slotAdded");
        },
        getData: function () {
            return _.filter(this.calendar.getSlots(), function (slot) {
                return (slot.get("status") === "Unknown");
            }, this);
        }
    });

    _.extend(ns.RammetidCalendar.prototype, ns.SlotClickMixin);

}(Flod));