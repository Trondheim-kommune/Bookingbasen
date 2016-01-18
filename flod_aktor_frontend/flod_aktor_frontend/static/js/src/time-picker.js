var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var OptionView = Backbone.View.extend({

        tagName: "option",

        initialize: function () {
        },

        render: function () {
            this.$el.html(this.model.get("moment").format("HH.mm"));
            return this;
        }
    });

    ns.TimePicker = Backbone.View.extend({

        tagName: "form",

        className: "form-inline",

        template: $("#timepicker_template").html(),

        events: {
            "change #fromSelect": "fromSelectChanged",
            "change #toSelect": "toSelectChanged"
        },

        initialize: function () {
            this.start_times = new Backbone.Collection();
            this.end_times = new Backbone.Collection();
        },

        fromSelectChanged: function (e) {
            this.start_time = this.start_times.get(e.target.selectedIndex).get("moment");
        },

        toSelectChanged: function (e) {
            this.end_time = this.end_times.get(e.target.selectedIndex).get("moment");
        },

        render: function (from, to) {
            this.start_time = moment(from);
            this.end_time = moment(from).add(30, "minutes");
            this.$el.append(_.template(this.template));
            var diff = to.diff(from, "minutes") / 30;
            this.start_times.reset(_.map(_.range(0, diff + 1), function (i) {
                return new Backbone.Model({
                    "id": i,
                    "moment": moment(from).add(i * 30, "m")
                });
            }));

            this.end_times.reset(_.map(_.range(0, diff), function (i) {
                return new Backbone.Model({
                    "id": i,
                    "moment": moment(from).add((i * 30) + 30, "m")
                });
            }));
            this.$("#fromSelect").append(this.start_times.map(function (model) {return new OptionView({"model": model}).render().$el; }));
            this.$("#toSelect").append(this.end_times.map(function (model) {return new OptionView({"model": model}).render().$el; }));
            return this;
        }
    });

}(Flod));