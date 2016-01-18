var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.ExportOverviewView = Backbone.View.extend({

        events: {
            "click .btn": "exportdata"
        },

        el: "#export",

        exportdata: function (e) {
            e.preventDefault();

            var selectedValues = [];
            $("#id_lokaler :selected").each(function () {
                selectedValues.push($(this).val());
            });

            if (this.$("#start_date").val() && this.$("#end_date").val() && selectedValues) {
                var start_date = moment(this.$("#start_date").val(), "DD.MM.YYYY").format("YYYY-MM-DD");
                var end_date = moment(this.$("#end_date").val(), "DD.MM.YYYY").format("YYYY-MM-DD");
                var url = '/api/booking/v1/organisations/export/period_overview/' + selectedValues.toString() + '/' + start_date + '/' + end_date + '/';
                window.open(url, '_blank');
            }
        },

        render: function () {
            return this;
        }
    });

    ns.createExportOverviewView = function (options) {
        return new ns.ExportOverviewView(options);
    };
})(Flod);
