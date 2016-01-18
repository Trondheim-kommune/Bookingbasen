var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.CalendarModel = Backbone.Model.extend({

        defaults: {
            "slot_duration": 30,
            "calendar_start": moment("08:00", "HH:mm"),
            "calendar_end": moment("23:00", "HH:mm"),
            "editable": false
        },

        constructor: function(attributes, options) {
            var rows = [];
            if (attributes) {
                rows = attributes.rows;
            }
            Backbone.Model.apply(this, [_.omit(attributes, "rows"), options]);
            this.set({"rows": this.mapRows(rows)});
            _.each(this.get("rows"), this.registerRow, this);
        },

        registerRow: function (row) {
            row.on("emptySlotClick", this.clickEmptySlot, this);
            row.on("slotClick", this.clickSlot, this);
            row.on("slotChanged", this.slotChanged, this);
            row.on("destroy", this.removeRow, this);
            row.on("add", this.addToRow, this);
        },

        addToRow: function (e) {
            this.trigger("slotAdded", e);
        },

        clickEmptySlot: function (e) {
            this.trigger("emptySlotClick", e);
        },

        clickSlot: function (e) {
            this.trigger("slotClick", e);
        },

        slotChanged: function (e) {
            this.trigger("slotChanged", e);
        },

        removeRow: function (row) {
            row.off("emptySlotClick", this.clickEmptySlot, this);
            row.off("slotClick", this.clickSlot, this);
            row.off("slotChanged", this.slotChanged, this);
            row.off("destroy", this.removeRow, this);
            var rows = _.without(this.get("rows"), row);
            this.set("rows", rows);
            this.trigger("reset");
        },

        mapRows: function (rowData) {

            var config = this.getConfig();
            return _.map(rowData, function (row) {
                if (row instanceof ns.CalendarRow) {
                    row.options = _.extend(row.options, config);
                    return row;
                }
                return new ns.CalendarRow(
                    row.slots,
                    _.omit(_.extend(row, config), "slots")
                );
            });
        },

        getConfig: function () {
            return {
                "slot_duration": this.get("slot_duration"),
                "calendar_start": this.get("calendar_start"),
                "calendar_end": this.get("calendar_end"),
                "editable": this.get("editable")
            };
        },

        row: function (index) {
            return this.get("rows")[index];
        },

        reset: function (rows) {
            rows = rows || [];
            this.set({"rows": this.mapRows(rows)});
            _.each(this.get("rows"), this.registerRow, this);
            this.trigger("reset");
        },

        getSlots: function () {
            return _.flatten(_.map(this.get("rows"), function (row) {
                return row.models;
            }));
        },

        addRow: function (row, index) {
            row =  this.mapRows([row])[0];

            if (!index) {
                this.get("rows").push(row);
            } else {
                this.get("rows").splice(index, 0, row);
            }
            this.registerRow(row);
            this.trigger("reset");
            return row;
        },

        addRows: function (rows) {
            if (!_.isArray(rows)) {
                rows = [rows];
            }
            rows =  this.mapRows(rows);
            var existing = this.get("rows");
            this.set("rows", existing.concat(rows));
            _.each(this.get("rows"), this.registerRow, this);
            this.trigger("reset");
            return rows;
        },

        getIndexForRow: function (row) {
            return _.indexOf(this.get("rows"), row);
        },

        getRowForDate: function (date) {
            return _.find(this.get("rows"), function (row) {
                return row.date.isSame(moment(date), "day");
            });
        },

        getRowForWeekday: function (weekday) {
            return _.find(this.get("rows"), function (row) {
                return row.date.isoWeekday() == weekday;
            });
        }
    });

}(Flod));