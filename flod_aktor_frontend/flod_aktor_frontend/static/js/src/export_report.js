var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.ExportReportView = Backbone.View.extend({

        events: {
            "click .btn": "exportdata"
        },

        el: "#export",

        exportdata: function (e) {
            e.preventDefault();
            var url = '/api/organisations/v1/export/organisations/';
            window.open(url, '_blank');
        },

        render: function () {
            return this;
        }
    });

    ns.createExportReportView = function (options) {
        return new ns.ExportReportView(options);
    };
})(Flod);
