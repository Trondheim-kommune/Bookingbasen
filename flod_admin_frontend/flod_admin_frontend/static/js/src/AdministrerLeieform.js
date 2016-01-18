var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.Settings = Backbone.Model.extend({
        url: "/api/booking/v1/adm_leieform/"

    });

    ns.LeieformSettingsView = Backbone.View.extend({
        template: $("#leieform_template").html(),

        events: {
            "click #save_button": "save"
        },

        initialize: function (options) {
            _.bindAll(this, "success", "error");
        },

        render: function () {
            this.$el.html(_.template(this.template)(this.model.toJSON()));

            this.setUpDatepicker("#deadline_date_div", this.model.get("repeating_booking_deadline"));
            this.setUpDatepicker("#repeating_enddate_div", this.model.get("repeating_booking_enddate"));
            this.setUpDatepicker("#single_enddate_div", this.model.get("single_booking_enddate"));

            return this;
        },

        setUpDatepicker: function (div, value) {
            this.$(div).datepicker({
                "format": 'dd.mm.yyyy',
                "weekStart": 1,
                "autoclose": true
            });

            if (value) {
                this.$(div).datepicker('setDate', moment(value, "YYYY-MM-DD").toDate());
            }
        },

        getFormData: function () {
            var deadline_date = this.$el.find("#deadline_date").val();
            var repeating_enddate = this.$el.find("#repeating_enddate").val();
            var single_enddate = this.$el.find("#single_enddate").val();

            this.model.set({
                'repeating_booking_allowed': this.$("#repeating_booking_allowed").is(':checked'),
                'single_booking_allowed': this.$("#single_booking_allowed").is(':checked'),
                'strotime_booking_allowed': this.$("#strotime_booking_allowed").is(':checked'),
                'repeating_booking_deadline': (deadline_date) ? moment(deadline_date, "DD.MM.YYYY").format("YYYY-MM-DD") : null,
                'repeating_booking_enddate': (repeating_enddate) ? moment(repeating_enddate, "DD.MM.YYYY").format("YYYY-MM-DD") : null,
                'single_booking_enddate': (single_enddate) ? moment(single_enddate, "DD.MM.YYYY").format("YYYY-MM-DD") : null
            });
        },

        save: function (e) {
            e.preventDefault();
            this.getFormData();
            this.model.save(null,
                {
                    success: this.success,
                    error: this.error
                }
            );
        },

        success: function () {
            this.$("#error_div").append(
                new ns.Notifier().render("Suksess!", "Leieform ble lagret.", "success", 5).$el
            );
        },

        error: function (model, xhr, options) {
            var error = JSON.parse(xhr.responseText);
            var errorString = error["__error__"].join(", ");
            this.$("#error_div").after(
                new ns.Notifier().render(
                    "En feil oppstod:",
                    error.message || errorString,
                    "error",
                    10
                ).$el
            );
        }
    });

}(Flod));