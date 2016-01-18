var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var ApplicationTableRowView = Backbone.View.extend({

        tagName: "tr",

        template: $("#application_table_row_template").html(),

        render: function () {
            this.$el.addClass(this.model.getClass());
            this.$el.html(_.template(this.template, this.model.toSimpleDisplay()));
            return this;
        }
    });

    var ApplicationTable = Backbone.View.extend({

        tagName: "table",

        className: "table table-bordered",

        template: $("#application_table_template").html(),

        render: function () {
            this.$el.html(_.template(this.template));
            this.$el.append(this.collection.map(function (model) {
                return new ApplicationTableRowView({"model": model}).render().$el;
            }));
            return this;
        }
    });

    ns.ApplicationList = Backbone.Collection.extend({
        model: ns.SimpleApplication,

        comparator: function (model) {
            return -moment(model.get("application_time")).valueOf();
        }
    });

    ns.ApplicationListView = Backbone.View.extend({

        render: function () {
            if (this.collection.length) {
                var table = new ApplicationTable({"collection": this.collection}).render();
                this.$el.html(table.$el);
            } else {
                this.$el.html('<div class="alert alert-info">Det er ingen søknader i systemet.</div>');
            }
            return this;
        }
    });

}(Flod));