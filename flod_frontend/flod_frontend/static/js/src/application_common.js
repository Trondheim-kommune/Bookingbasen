var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";
    ns.application_status_map = {
        "Pending": {"name": "Avventer behandling", "class": "warning"},
        "Processing": {"name": "Under behandling", "class": "info" },
        "Granted": {"name": "Godkjent", "class": "success"},
        "Denied": {"name": "Avvist", "class": "error"}
    };

    ns.capitaliseFirstLetter = function (input) {
        return input.charAt(0).toUpperCase() + input.slice(1);
    };

    ns.getTextualWeekDay = function (weekDayNumber) {
        if (weekDayNumber === 7) {
            return moment.fn._lang._weekdays[0];
        } else {
            return moment.fn._lang._weekdays[weekDayNumber];
        }
    };

    ns.formatSlotRepeating = function (slot) {
        var repeatingFormat = "<%= day %>er <%= start_date %> - <%= end_date %><br /><i class='icon-time'></i> <%= start_time %> - <%= end_time %>";
        return _.template(repeatingFormat, {
            day:  ns.capitaliseFirstLetter(ns.getTextualWeekDay(slot.week_day)),
            start_time: moment(slot.start_time, "HH.mm.ss").format("HH:mm"),
            end_time: moment(slot.end_time, "HH.mm.ss").format("HH:mm"),
            start_date: moment(slot.start_date, "YYYY-MM-DD").format("DD.MM.YYYY"),
            end_date: moment(slot.end_date, "YYYY-MM-DD").format("DD.MM.YYYY")
        });
    };

    ns.formatSlotSingle = function (slot) {
        var singleFormat = "<%= day %> <br /><i class='icon-time'></i> <%= start_time %>  - <%= end_time %>";
        return _.template(singleFormat, {
            day:  ns.capitaliseFirstLetter(moment(slot.start_time).format("dddd DD.MM.YYYY")),
            start_time: moment(slot.start_time).format("HH:mm"),
            end_time: moment(slot.end_time).format("HH:mm")
        });
    };

    ns.formatSlot = function (slot, type) {
        if (type === "repeating") {
            return ns.formatSlotRepeating(slot);
        } else {
            return ns.formatSlotSingle(slot);
        }
    };

}(Flod));