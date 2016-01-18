var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.LegendView = Backbone.View.extend({

        tagName: "table",

        className: "table table-bordered legend",

        render: function () {
            var rows = _.map(this.options.statuses, function (status) {
                return $("<tr><td class='" + status.status + "'></td><td>" + status.text + "</td></tr>");
            });
            this.$el.append(rows);
            return this;
        }

    });

}(Flod));
