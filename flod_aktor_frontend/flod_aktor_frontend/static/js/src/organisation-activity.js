var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";


    var ActivityView = Backbone.View.extend({

        tagName: "li",

        template: $("#activity_chooser_element_template").html(),

        events: {
            "click .icon-remove": "remove"
        },

        initialize: function () {
            _.bindAll(this, "remove");
        },

        render: function () {
            this.$el.html(_.template(this.template, this.model.toJSON()));
            return this;
        },

        remove: function () {
            this.model.collection.remove(this.model);
            Backbone.View.prototype.remove.apply(this, arguments);
        }
    });

    ns.ActivityTypeChooser = Backbone.View.extend({

        events: {
            "click #add_activity": "addActivity"
        },

        initialize: function () {
            _.bindAll(this, "addActivity");
            this.collection = new Backbone.Collection();

            this.collection.on("add", this.showActivity, this);
        },

        addActivity: function () {
            var selected = parseInt(this.$("#id_type_activity").val(), 10);
            if (selected) {
                var activity = _.find(this.options.activities, function (activity) {
                    return activity.id === selected;
                });
                if (!this.collection.find(function (activityModel) {return (activityModel.get("id") === activity.id); })) {
                    var model = new Backbone.Model(activity);
                    this.collection.add(model);
                }
            }
        },

        showActivity: function (model) {
            this.$("#activity_list").append(new ActivityView({"model": model}).render().$el);
        },

        selectActivities: function (activities) {
            activities = _.filter(this.options.activities, function (activity) {
                return (activities.indexOf(activity.id) !== -1);
            });
            this.collection.add(activities);
        }
    });

}(Flod));