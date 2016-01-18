var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    if (!ns.TimeSlot) {
        ns.TimeSlot = Backbone.Model;
    }

    var Slot = ns.TimeSlot.extend({
        getDisplayName: function () {
            return ns.TimeSlot.prototype.getDisplayName.apply(this, arguments) +
                " (søknad #" + this.get("application") + ")";
        }
    });

    var status_map = {
        "Pending": {"name": "Avventer behandling", "class": "warning", "key": "Pending"},
        "Processing": {"name": "Behandles", "class": "warning", "key": "Processing"},
        "Granted": {"name": "Godkjent", "class": "success", "key": "Granted"},
        "Denied": {"name": "Avvist", "class": "error", "key": "Denied"}
    };

    function setStatus(status, slots) {
        _.each(slots, function (slot) {
            slot.status = status;
        });
        return slots;
    }

    function getTypeText(application) {

        if (application.typeMapping[application.get('type')]) {
            return application.typeMapping[application.get('type')];
        }
        return "-";
    }

    ns.Application = ns.SimpleApplication.extend({

        url: function () {
            var base = "/api/booking/v1/applications/";
            if (!this.isNew()) {
                base += this.get("id");
            }
            return base;
        },

        getStartAndEndDate: function () {
            var slot0 = this.get("slots")[0];
            return {
                start_date: this.formatDate(slot0.start_date),
                end_date: this.formatDate(slot0.end_date)
            };
        },

        formatDate: function (date) {
            var format = "DD.MM.YYYY";
            return moment(date).format(format)
        },

        nvl: function (data, null_value) {
            return data ? data : null_value;
        },

        isAfter: function (date) {
            var oks = _.map(this.get("slots"), function (slot) {
                if (slot.end_date) {
                    return moment(slot.end_date, "YYYY-MM-DD").isAfter(date);
                } else {
                    return moment(slot.end_time).isAfter(date);
                }
            });
            return (oks.indexOf(true) !== -1);
        },

        toDetailDisplay: function () {

            var can_release = (
            (this.get('type') === 'repeating') &&
            this.get("status") === 'Granted' &&
            this.get("resource").is_deleted === false &&
            this.get("resource").is_published === true &&
            this.isAfter(moment()));

            var data = {
                "facility": {
                    "name": this.get("resource").name,
                    "facilitations": {
                        "amenities": this.nvl(this.get("resource").amenities, {}),
                        "equipment": this.nvl(this.get("resource").equipment, {}),
                        "accessibility": this.nvl(this.get("resource").accessibility, {}),
                        "suitability": this.nvl(this.get("resource").suitability, {}),
                        "facilitators": this.nvl(this.get("resource").facilitators, {})
                    }
                },
                "facility_id": this.get("resource").id,
                "requested_facility": {
                    "name": this.get("requested_resource").name,
                    "facilitations": {
                        "amenities": this.nvl(this.get("requested_resource").amenities, {}),
                        "equipment": this.nvl(this.get("requested_resource").equipment, {}),
                        "accessibility": this.nvl(this.get("requested_resource").accessibility, {}),
                        "suitability": this.nvl(this.get("requested_resource").suitability, {}),
                        "facilitators": this.nvl(this.get("requested_resource").facilitators, {})
                    }
                },
                "text": this.get("text"),
                "comment": this.get("comment"),
                "facilitation": this.get("facilitation"),
                "facilitations": {
                    "amenities": this.nvl(this.get("amenities"), {}),
                    "equipment": this.nvl(this.get("equipment"), {}),
                    "accessibility": this.nvl(this.get("accessibility"), {}),
                    "suitability": this.nvl(this.get("suitability"), {}),
                    "facilitators": this.nvl(this.get("facilitators"), {})
                },
                "requested_facilitations": {
                    "amenities": this.nvl(this.get("requested_amenities"), {}),
                    "equipment": this.nvl(this.get("requested_equipment"), {}),
                    "accessibility": this.nvl(this.get("requested_accessibility"), {}),
                    "suitability": this.nvl(this.get("requested_suitability"), {}),
                    "facilitators": this.nvl(this.get("requested_facilitators"), {})
                },
                "showEdit": (["Pending", "Processing"].indexOf(this.get("status")) !== -1),
                "status": status_map[this.get("status")],
                "resource_is_deleted": this.get("resource").is_deleted,
                "resource_is_published": this.get("resource").is_published,
                "type": this.get('type'),
                "type_formatted": getTypeText(this),
                "is_arrangement": this.get('is_arrangement'),
                "person": this.get('person'),
                "can_release": can_release,
                "application_date": this.formatDate(this.get('application_time'))
            };

            data.times = _.map(this.get("slots"), function (slot) {
                return ns.formatSlot(slot, this.get('type'));
            }, this);
            data.requested_times = _.map(this.get("requested_slots"), function (slot) {
                return ns.formatSlot(slot, this.get('type'));
            }, this);

            var organisation = this.get("organisation");
            if (organisation) {
                data.organisation = organisation.name;
                data.num_members = organisation.num_members;
                data.organisation_is_deleted = organisation.is_deleted;
            } else {
                data.organisation = "n/a";
                data.num_members = "n/a";
                data.organisation_is_deleted = false;
            }
            return data;
        },

        getSlots: function () {
            if (this.slots) {
                return this.slots;
            }

            var slots = this.get("slots");
            setStatus(this.get("status"), slots);

            this.slots = _.map(slots, function (slot) {
                var slotModel = new Slot(slot);
                slotModel.type = this.getType();
                slotModel.set({
                    "application": this.get("id"),
                    "organisation": this.get("organisation"),
                    "person": this.get("person")
                });
                return slotModel;
            }, this);

            var canEditSlots = !(this.get("status") === "Granted" ||
            this.get("status") === "Denied");
            if (!canEditSlots) {
                _.each(this.slots, function (slot) {
                    slot.set("editable", false);
                });
            }
            return this.slots;
        }
    });

    ns.ApplicationList = Backbone.Collection.extend({
        model: ns.Application,

        comparator: function (model) {
            return -moment(model.get("application_time")).valueOf();
        }
    });

}(Flod));
