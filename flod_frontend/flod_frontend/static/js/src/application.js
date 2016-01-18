var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var Application = Backbone.Model.extend({

        "url": "/api/booking/v1/applications/",

        parse: function (response) {
            if (response.organisation) {
                if (!response.organisation.uri) {
                    response.organisation = null;
                }
            }
            return response;
        },

        getDisplayData: function () {

            return {
                "slots": this.get("slots"),
                "person": this.get("person").toJSON(),
                "resource": this.get("resource").get("name"),
                "text": this.get("text"),
                "facilitation": this.get("facilitation"),
                "facilitations": {
                    "amenities": this.get("amenities"),
                    "accessibility": this.get("accessibility"),
                    "equipment": this.get("equipment"),
                    "suitability": this.get("suitability"),
                    "facilitators": this.get("facilitators")
                },
                "organisation": this.get("organisation")
            };
        },

        toJSON: function () {
            var data = {
                "person": {"uri": this.get("person").get("uri")},
                "text": this.get("text"),
                "facilitation": this.get("facilitation"),
                "amenities": this.get("amenities"),
                "accessibility": this.get("accessibility"),
                "equipment": this.get("equipment"),
                "suitability": this.get("suitability"),
                "facilitators": this.get("facilitators"),
                "resource": {"uri": this.get("resource").get("uri")}
            };
            if (this.has("organisation")) {
                data.organisation = {"uri": this.get("organisation").uri};
            }

            data.slots = this.serializeSlots();
            return data;
        }
    });

    ns.RepeatingApplication = Application.extend({

        "url": "/api/booking/v1/applications/repeating/",

        slot_type: "requested_repeating_slots",

        serializeSlots: function () {
            return _.map(this.get("slots"), function (slot) {
                return {
                    "start_time": moment(slot.get("start_time")).format("HH:mm:ss"),
                    "end_time": moment(slot.get("end_time")).format("HH:mm:ss"),
                    "start_date": moment(this.get("start_date")).format("YYYY-MM-DD"),
                    "end_date": moment(this.get("end_date")).format("YYYY-MM-DD"),
                    "week_day": slot.get("start_time").isoWeekday()
                };
            }, this);
        },

        getDisplayData: function () {
            var data = Application.prototype.getDisplayData.apply(this, arguments);
            data.start_date = moment(this.get("start_date")).format("DD.MM.YYYY");
            data.end_date = moment(this.get("end_date")).format("DD.MM.YYYY");
            return data;
        }
    });

    ns.SingleApplication = Application.extend({

        slot_type: "requested_slots",

        "url": "/api/booking/v1/applications/single/",

        serializeSlots: function () {
            return _.map(this.get("slots"), function (slot) {
                return {
                    "start_time": moment(slot.get("start_time")).format("YYYY-MM-DDTHH:mm:ss"),
                    "end_time": moment(slot.get("end_time")).format("YYYY-MM-DDTHH:mm:ss")
                };
            }, this);
        }
    });

}(Flod));