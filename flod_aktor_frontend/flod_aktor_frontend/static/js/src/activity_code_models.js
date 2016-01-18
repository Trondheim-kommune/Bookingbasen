var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var BrregActivityCode = Backbone.Model.extend({

        initialize: function () {

            var flod_activity_types = this.get("flod_activity_types");
            this.set("flod_activity_types", new ns.ActivityTypes(flod_activity_types));

        }
    });

    ns.BrregActivityCodes = Backbone.Collection.extend({

        model: BrregActivityCode,

        getByCodes: function (codes) {
            return new ns.BrregActivityCodes(this.filter(function (activityCode) {
                return codes.indexOf(activityCode.get("code")) !== -1;
            }));
        },

        getActivityTypes: function () {

            return new ns.ActivityTypes(_.flatten(this.map(function (model) {
                return model.get("flod_activity_types").models;
            })));
        },

        toDisplay: function () {
            return this.map(function (model) {
                return model.get("description") + " (" + model.get("code") + ")";
            });
        }

    });

    ns.ActivityTypes = Backbone.Collection.extend({});

}(Flod));