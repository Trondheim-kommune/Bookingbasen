var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var getTextualWeekDay = function (weekDayNumber) {
        return moment().isoWeekday(weekDayNumber).format("dddd");
    };

    var capitaliseFirstLetter = function (input) {
        return input.charAt(0).toUpperCase() + input.slice(1);
    };

    function formatSlot(slot) {
        var repeatingFormat = "<%= day %>er: <%= start_time %>  - <%= end_time %> (<%= start_date %> - <%= end_date %>)";
        return _.template(repeatingFormat, {
            day:  capitaliseFirstLetter(getTextualWeekDay(slot.week_day)),
            start_time: moment(slot.start_time, "HH.mm.ss").format("HH:mm"),
            end_time: moment(slot.end_time, "HH.mm.ss").format("HH:mm"),
            start_date: moment(slot.start_date, "YYYY-MM-DD").format("DD.MM.YYYY"),
            end_date: moment(slot.end_date, "YYYY-MM-DD").format("DD.MM.YYYY")
        });
    }

    ns.SingleRammetidView = Backbone.View.extend({
        template: $("#single_rammetid_template").html(),
        events: {
            "click #delete": "delete"
        },
        initialize: function () {
            _.bindAll(this, "delete", "deleteSuccess", "deleteError");
        },
        render: function () {
            var times = _.map(this.model.getSlots(), function (slot) {
                return formatSlot(slot);
            }, this);
            var data = {
                "resource": this.model.get("resource").name,
                "times": times
            };
            this.$el.html(_.template(this.template, data));
            return this;
        },
        'delete': function () {
            var self = this;
            // If yes button is clicked in the delete dialog
            $('#btnYes').click(function () {
                self.model.destroy({
                    success: self.deleteSuccess,
                    error: self.deleteError
                });
            });
        },
        deleteSuccess: function (model, response) {
            window.location.href = "/rammetid";
        },
        deleteError: function (model, response) {

        }
    });

}(Flod));
