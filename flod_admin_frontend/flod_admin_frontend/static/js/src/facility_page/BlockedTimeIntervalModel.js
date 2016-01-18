var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.BlockedTimeInterval = Backbone.Model.extend({
        url: function () {
            var id = "";
            if (!this.isNew()) {
                id = this.get("id");
            }
            return "/api/booking/v1/blockedtimeintervals/" + id;
        },

        validate : function (attrs, options) {
            var errors = [];

            function isDateValid(date) {
                return !_.isUndefined(date) && date.trim() && moment(date, "YYYY-MM-DDThh:mm").isValid();
            }

            var startTimeOk = false;
            if (!isDateValid(this.get('start_time'))) {
                errors.push({
                    id: "blocked_time_interval_form",
                    message: "Du må angi en startdato.",
                    type: "error"
                });
            } else {
                startTimeOk = true;
            }

            var endTimeOk = false;
            if (!isDateValid(this.get('end_time'))) {
                errors.push({
                    id: "blocked_time_interval_form",
                    message: "Du må angi en sluttdato.",
                    type: "error"
                });
            } else {
                endTimeOk = true;
            }

            if (startTimeOk && endTimeOk) {
                var startTime = moment(this.get("start_time"));
                var endTime = moment(this.get("end_time"));

                if (!startTime.isBefore(endTime)) {
                    errors.push({
                        id: "blocked_time_interval_form",
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

            if (errors.length > 0) {
                return errors;
            }
        },

        splitDatetimes: function () {
            return {
                "start_time": moment(this.get("start_time")).format("HH:mm"),
                "end_time": moment(this.get("end_time")).format("HH:mm"),
                "start_date": moment(this.get("start_time")).format("DD.MM.YYYY"),
                "end_date": moment(this.get("end_time")).format("DD.MM.YYYY"),
                "note": this.get("note")
            };
        }
    });

    ns.BlockedTimeIntervalCollection = Backbone.Collection.extend({
        model: ns.BlockedTimeInterval,
        url: function () {
            return "/api/booking/v1/blockedtimeintervals/?resource_uri=" + this.resource_uri;
        },

        initialize: function (models, options) {
            options = options || {};
            if (options.resource_uri) {
                this.resource_uri = options.resource_uri;
            }
        }
    });
}(Flod));
