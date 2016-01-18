var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var capitaliseFirstLetter = function (input) {
        return input.charAt(0).toUpperCase() + input.slice(1);
    };

    ns.WeeklyBlockedTime = Backbone.Model.extend({
        url: function () {
            var id = "";
            if (!this.isNew()) {
                id = this.get("id");
            }
            return "/api/booking/v1/weeklyblockedtimes/" + id;
        },

        validate : function (attrs, options) {

            function isUnset(value) {
                return (_.isUndefined(value) || !value.trim());
            }

            var check = {
                "start_time": "Du må angi et starttidspunkt.",
                "end_time": "Du må angi et sluttidspunkt.",
                "start_date": "Du må angi en startdato.",
                "end_date": "Du må angi en sluttdato."
            };

            var errors = _.compact(_.map(check, function (error, key) {
                if (isUnset(this.get(key))) {
                    return {
                        id: key,
                        message: error,
                        type: "error"
                    };
                }
            }, this), this);

            if (!_.findWhere(errors, {"id": "start_time"}) && !_.findWhere(errors, {"id": "end_time"})) {
                var startTime = moment(this.get("start_time"), "HH:mm");
                var endTime = moment(this.get("end_time"), "HH:mm");

                if (!startTime.isBefore(endTime)) {
                    errors.push({
                        id: "start_time",
                        message: "Starttidspunkt må være før sluttidspunkt.",
                        type: "error"
                    });
                }

                _.map({"start_time": startTime,"end_time": endTime}, function (time, key) {
                    var minutes = time.minutes();
                    if (_.indexOf([0,30], minutes) == -1) {
                        errors.push({
                        id: key,
                        message: "Tiden må være angitt i hele halvtimer",
                        type: "error"
                    });
                    }
                });

            }

            if (!_.findWhere(errors, {"id": "start_date"}) && !_.findWhere(errors, {"id": "end_date"})) {

                var startDate = moment(this.get("start_date"));
                var endDate = moment(this.get("end_date"));

                if (startDate.isAfter(endDate)) {
                    errors.push({
                        id: "start_date",
                        message: "Startdato må være før sluttdato.",
                        type: "error"
                    });
                }
            }
            if (errors.length > 0) {
                return errors;
            }
        },

        toDisplay: function () {
            return {
                "week_day": capitaliseFirstLetter(moment().isoWeekday(this.get("week_day")).format("dddd") + "er"),
                "start_time": moment(this.get("start_time"), "HH:mm").format("HH:mm"),
                "end_time": moment(this.get("end_time"), "HH:mm").format("HH:mm"),
                "start_date": moment(this.get("start_date"), "YYYY-MM-DD").format("LL"),
                "end_date": moment(this.get("end_date"), "YYYY-MM-DD").format("LL"),
                "note": this.get("note")
            };
        }
    });

    ns.WeeklyBlockedTimeCollection = Backbone.Collection.extend({

        model: ns.WeeklyBlockedTime,

        url: function () {
            return "/api/booking/v1/weeklyblockedtimes/?resource_uri=" + this.resource_uri;
        },

        initialize: function (models, options) {
            options = options || {};
            if (options.resource_uri) {
                this.resource_uri = options.resource_uri;
            }
        }
    });

}(Flod));
