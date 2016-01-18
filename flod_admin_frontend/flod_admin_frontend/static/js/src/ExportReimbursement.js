var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.ExportReimbursementView = Backbone.View.extend({

        events: {
            "click .btn": "exportdata"
        },

        el: "#export",

        exportdata: function (e) {
            e.preventDefault();
            if (this.$("#start_date") && this.$("#end_date")) {
                var start_date = moment(this.$("#start_date").val(), "DD.MM.YYYY").format("YYYY-MM-DD");
                var end_date = moment(this.$("#end_date").val(), "DD.MM.YYYY").format("YYYY-MM-DD");
                var url = '/api/booking/v1/organisations/export/reimbursement/' + start_date + '/' + end_date + '/';
                window.open(url, '_blank');
            }
        },

        render: function () {
            return this;
        }
    });

    ns.createExportReimbursementView = function (options) {
        return new ns.ExportReimbursementView(options);
    };
})(Flod);
