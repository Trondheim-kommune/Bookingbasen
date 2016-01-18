var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.ButtonsView = Backbone.View.extend({
        template: $("#buttons_template").html(),

        initialize: function(options){
            var formatted_deadline = this.model.get('repeating_booking_deadline');

            if (this.model.get('repeating_booking_deadline')) {
                this.model.set('repeating_booking_deadline', moment(this.model.get("repeating_booking_deadline"), "YYYY-MM-DD").format('DD.MM.YYYY'));
            }

            if (this.model.get('repeating_booking_enddate')) {
                this.model.set('repeating_booking_enddate', moment(this.model.get("repeating_booking_enddate"), "YYYY-MM-DD").format('DD.MM.YYYY'));
            }

            if (this.model.get('single_booking_enddate')) {
                this.model.set('single_booking_enddate', moment(this.model.get("single_booking_enddate"), "YYYY-MM-DD").format('DD.MM.YYYY'));
            }
        },

        render: function () {
            this.$el.html(_.template(this.template) (this.model.toJSON()));
            return this;
        }
    });

}(Flod));