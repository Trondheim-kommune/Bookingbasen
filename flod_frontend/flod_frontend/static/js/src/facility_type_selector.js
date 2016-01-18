var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var OptionView = Backbone.View.extend({

        tagName: "option",

        events: {
            "select": "select"
        },

        initialize: function () {
            _.bindAll(this, "select");
        },

        render: function () {
            this.$el.html(this.model.get("name"));
            return this;
        },

        select: function () {
            this.model.trigger("select", this.model);
        }
    });

    ns.FacilityTypeSelector = Backbone.View.extend({

        tagName: "select",

        "id": "facility_typeSelect",

        events: {
            "change": "change"
        },

        initialize: function () {
            this.collection = new Backbone.Collection(this.collection);
            this.collection.on("select", this.selectType, this);
            _.bindAll(this, "change");
        },

        render: function () {
            var elems = this.collection.map(function (option) {
                return new OptionView({"model": option}).render().$el;
            });
            var none = $("<option selected>---</option>").on("select", _.bind(this.selectNone, this));
            elems.push(none);
            this.$el.append(elems);
            return this;
        },

        selectNone: function () {
            this.trigger("select", null);
        },

        selectType: function (type) {
            this.trigger("select", type.get("id"));
        },

        change: function () {
            this.$("option:selected").trigger("select");
        }
    });
}(Flod));