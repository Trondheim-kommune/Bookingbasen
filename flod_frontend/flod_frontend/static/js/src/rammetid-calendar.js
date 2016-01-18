var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.RammetidCalendar = ns.IdealizedWeeklyCalendarView.extend({
        initialize: function (options) {
            _.bindAll(this, "slotsFectched");
            ns.IdealizedWeeklyCalendarView.prototype.initialize.apply(this, arguments);
            this.calendar.on("slotClick", this.slotClicked, this);
            this.on("emptySlotClick", this.emptySlotClick, this);
            this.umbrellaOrganisation = options.umbrellaOrganisation;
            this.shown = false;
            this.calendarView.on("slotRemoved", this.slotRemoved, this);
        },

        slotRemoved: function() {
            var selectedSlots = _.filter(this.calendar.getSlots(), function (slot) {
                return slot.get('selected');
            });
            this.trigger("toggleSlotSelect", selectedSlots);
            this.trigger("slotRemoved");
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
            var rammetidSlots = new ns.RammetidSlots([], {
                resource_uri: this.data.resource.get("uri"),
                start_date: moment(this.data.dates.start_date).format("YYYY-MM-DD"),
                end_date: moment(this.data.dates.end_date).format("YYYY-MM-DD"),
                umbrella_organisation_uri: this.umbrellaOrganisation.get("uri")
            });

            var slots = new ns.RepeatingSlots([], {
                resource_uri: this.data.resource.get("uri"),
                start_date: moment(this.data.dates.start_date).format("YYYY-MM-DD"),
                end_date: moment(this.data.dates.end_date).format("YYYY-MM-DD"),
                status: "Granted"
            });

            var showSlots = _.after(2, _.bind(function () {
                this.slotsFectched(rammetidSlots, slots);
            }, this));

            rammetidSlots.fetch({"success": showSlots});
            slots.fetch({"success": showSlots});
        },
        slotsFectched: function (rammetidSlots, slots) {
            // filter slots with exact dates
            var rammetid = rammetidSlots.where(this.data.dates);
            var mappedRammetidSlots = rammetid.reduce(ns.mapSlotsByWeekday, {});
            var inverted = Flod.calendar.invertSlots(mappedRammetidSlots);
            _.each(inverted, function (slots, weekday) {
                var row = this.calendar.row(weekday - 1);
                if (row) {
                    row.addSlots(slots);
                }
            }, this);
            var self = this;
            var mappedSlots = slots.reduce(ns.mapSlotsByWeekday, {});
            _.each(mappedSlots, function (slots, weekday) {
                var row = this.calendar.row(weekday - 1);
                if (row) {
                    _.each(slots, function (slot) {
                        var memberOrganisation_uri = slot.get("organisation_uri");
                        var memberOrganisation = self.options.memberOrganisations.find(function (model) {
                            return model.get('organisation').uri === memberOrganisation_uri;
                        });
                        if (memberOrganisation) {
                            slot.set("color", memberOrganisation.get('color'));
                            slot.set("display_name", memberOrganisation.get('name'));
                        }
                        slot.set("editable", false);
                    });
                    row.addSlots(slots);
                }
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
            if (!this.data.memberOrganisation) {
                return;
            }

            var orgId = this.data.memberOrganisation.get('id');
            var row = data.row;
            //check to see if this slot can be merged with other new ones
            var other = row.filter(function (slot) {
                var isnew = (slot.get('status') === 'unsaved');
                var nextTo = ns.isNextTo(data, slot);
                var sameOrg = (slot.get('org_id') === orgId);
                return (isnew && nextTo && sameOrg);
            });
            if (other.length) {
                data = ns.extendData(data, other);
                _.each(other, function (slot) {
                    row.removeSlot(slot);
                });
            }
            row.addSlot(new Flod.TimeSlot(_.extend(data, {
                org_id: orgId,
                color: this.data.memberOrganisation.get('color'),
                status: 'unsaved'
            })));
            this.trigger("slotAdded");
        },
        slotClicked: function (slot) {
            var canRedirect = slot.has("rammetid_id");
            if (canRedirect) {
                window.location.href = "/rammetid/" + slot.get("rammetid_id");
            }
        },
        getData: function () {
            return _.filter(this.calendar.getSlots(), function (slot) {
                return (slot.get("status") === "unsaved");
            }, this);
        }
    });

    _.extend(ns.RammetidCalendar.prototype, ns.SlotClickMixin);

}(Flod));