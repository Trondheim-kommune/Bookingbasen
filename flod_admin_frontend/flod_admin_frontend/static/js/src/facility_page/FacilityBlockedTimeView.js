var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.FacilityBlockedTimeView = Backbone.View.extend({

        initialize: function () {
            // Weekly Blocked Time: recurring every week between start and end date
            var weeklyBlockedTimeCollection = new Flod.WeeklyBlockedTimeCollection();
            var weeklyBlockedTimeView = new Flod.WeeklyBlockedTimeView({
                editable: this.options.editable,
                model: this.model,
                collection: weeklyBlockedTimeCollection,
                el: this.$('#weekly_blocked_time')
            });

            var eightToFourView = new Flod.WeeklyBlockedTimeEightToFourView({
                editable: this.options.editable,
                model: this.model,
                collection: weeklyBlockedTimeCollection,
                el: this.$('#weekly_blocked_time_eight_to_four')
            });

            if (!this.model.isNew()) {
                weeklyBlockedTimeCollection.resource_uri = this.model.get('uri');
                weeklyBlockedTimeCollection.fetch();
            }

            // Blocked Time Interval: blocking between two datetimes
            var blockedTimeIntervalCollection = new Flod.BlockedTimeIntervalCollection();
            var blockedTimeIntervalView = new Flod.BlockedTimeIntervalView({
                editable: this.options.editable,
                model: this.model,
                collection: blockedTimeIntervalCollection,
                el: this.$('#blocked_time_interval')
            });

            if (!this.model.isNew()) {
                blockedTimeIntervalCollection.resource_uri = this.model.get('uri');
                blockedTimeIntervalCollection.fetch();
            }
        }
    });

}(Flod));