var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    function parseTime(string) {
        var time = moment(string);
        if (time.isValid()) {
            return time;
        }
        return moment(string, "HH:mm:ss");
    }

    ns.TimeSlot = Backbone.Model.extend({

        defaults: {
            "resource": null,
            "start_time": null,
            "end_time": null,
            "organisation": null,
            "person": null,
            "status": "Unknown",
            "label": ""
        },

        parse: function (attributes) {

            if (attributes) {
                var data = _.clone(attributes);
                if (data.start_time) {
                    data.start_time = parseTime(data.start_time);
                }
                if (data.end_time) {
                    data.end_time = parseTime(data.end_time);
                }
                return data;
            }
            return null;
        },

        constructor: function (attributes, options) {
            Backbone.Model.apply(this, [this.parse(attributes), options]);
        },

        getDisplayName: function () {
            if (this.has("display_name")) {
                return this.get("display_name");
            } else {
                return this.getAktorName();
            }
        },

        getAktorName: function(){
            if (this.has("organisation") && this.get("organisation").name) {
                return this.get("organisation").name;
            } else if (this.has("person") && (this.get("person") instanceof Backbone.Model) && this.get("person").has("name")) {
                return this.get("person").get("name");
            } else if (this.has("person") && this.get("person").name) {
                return this.get("person").name;
            } else if (this.has("person") && this.get("person").first_name && this.get("person").last_name) {
                return this.get("person").last_name + ", " + this.get("person").first_name;
            }
            return "";
        },

        getStatus: function () {
            return this.get("status").toLowerCase();
        },

        getLabel: function() {
            if (this.get("status") == "Unknown"){
                return "";
            }

            var label = (this.has("display_name")) ? this.get("display_name").split('(')[0] : this.getAktorName();
            return label;
        },

        getRange: function () {
            return moment().range(this.get("start_time"), moment(this.get("end_time")));
        },

        toJSON: function () {
            var attributes = Backbone.Model.prototype.toJSON.apply(this, arguments);
            attributes.start_time = moment(this.get("start_time")).format("YYYY-MM-DDTHH:mm:ss");
            attributes.end_time = moment(this.get("end_time")).format("YYYY-MM-DDTHH:mm:ss");

            if (this.get("person") instanceof Backbone.Model) {
                attributes.person = {"uri": this.get("person").get("uri")};
            } else {
                attributes.person = {"uri": this.get("person").uri};
            }

            attributes.resource = {"uri": this.get("resource").uri};
            if (attributes.organisation) {
                if (!attributes.organisation.uri) {
                    attributes = _.omit(attributes, "organisation");
                }
            }

            return _.omit(attributes, "editable");
        },

        changeDate: function (date) {
            this.get("start_time").year(date.year()).month(date.month()).date(date.date());
            this.get("end_time").year(date.year()).month(date.month()).date(date.date());
            return this;
        },

        getDuration: function () {
            return this.get("end_time").diff(this.get("start_time"), "minutes");
        },

        collidesWith: function (timeSlot, own) {

            if (_.isEqual(this, timeSlot)) {                
                return false;
            }

            var range = this.getRange();
            if (range.contains(timeSlot.get("start_time"))) {
                return !(this.get("end_time").isSame(timeSlot.get("start_time")));
            }
            if (range.contains(timeSlot.get("end_time"))) {
                return !(this.get("start_time").isSame(timeSlot.get("end_time")));
            }
            if (!own) {
                return timeSlot.collidesWith(this, true);
            }
            return false;
        }
    });

}(Flod));