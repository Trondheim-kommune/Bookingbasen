var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";
    ns.Weeks = Backbone.Model.extend({

        getDisplayStr: function () {
            return "Uke " + this.get("week").get("week") + ", " + this.get("week").get("year");
        },

        getWeeks: function () {
            return [
                this.get("week").clone().prev(),
                this.get("week").clone(),
                this.get("week").clone().next()
            ];
        },

        next: function () {
            return this.get("week").clone().next();
        },

        nextMonth: function () {
            return this.get("week").clone().nextMonth();
        },

        prev: function () {
            return this.get("week").clone().prev();
        },

        prevMonth: function () {
            return this.get("week").clone().prevMonth();
        },

        hasPrev: function () {
            return true;
        },

        hasNext: function () {
            return true;
        }
    });
}(Flod));