var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var status_map = {
        "Pending": {"name": "Avventer behandling", "class": "warning"},
        "Processing": {"name": "Behandles", "class": "warning"},
        "Granted": {"name": "Godkjent", "class": "success"},
        "Denied": {"name": "Avvist", "class": "error"}
    };

    ns.SimpleApplication = Backbone.Model.extend({

        typeMapping: {
            "single": "Engangslån",
            "repeating": "Fast lån",
            "strotime": "Strøtime"
        },

        getSlotType: function () {
            return "slots";
        },

        getType: function () {
            return this.get("type");
        },

        toSimpleDisplay: function () {
            var times = _.map(this.get("slots"), function (slot) {
                return ns.formatSlot(slot, this.get('type'));
            }, this);

            return {
                "person_email_address": this.get("person").email_address,
                "facility": this.get("resource").name,
                "person": this.get("person").last_name + ", " + this.get("person").first_name,
                "application_time": moment(this.get("application_time")).format("DD.MM.YYYY"),
                "status": status_map[this.get("status")].name,
                "type": this.typeMapping[this.getType()],
                "id": this.get("id"),
                "showEdit": (this.get("status") === "Pending" || this.get("status") === "Processing"),
                "organisation": this.get("organisation").name,
                "resource_is_deleted": this.get("resource").is_deleted,
                "is_arrangement": this.get("is_arrangement"),
                "times": times,
                "organisation_is_deleted": this.get("organisation").is_deleted
            };
        },

        getClass: function () {
            return status_map[this.get("status")]["class"];
        }
    });

}(Flod));