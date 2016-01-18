var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var EditableViewMixin = {

        editable: true,

        toggleEditable: function (editable) {
            this.$("button").prop('disabled', !editable);
            this.$("input").prop('disabled', !editable);
            this.$("select").prop('disabled', !editable);
            this.$("textarea").prop('disabled', !editable);
        }
    };


    _.extend(ns.FacilityView.prototype, EditableViewMixin);
    _.extend(ns.FacilityGeocodingView.prototype, EditableViewMixin);
    _.extend(ns.FacilityImageMainView.prototype, EditableViewMixin);
    _.extend(ns.FacilityDocumentsMainView.prototype, EditableViewMixin);
    _.extend(ns.RentalTypesView.prototype, EditableViewMixin);
    _.extend(ns.FacilityBlockedTimeView.prototype, EditableViewMixin);
    _.extend(ns.FacilityAdministratorView.prototype, EditableViewMixin);
    _.extend(ns.FacilityInternalNotesView.prototype, EditableViewMixin);
    _.extend(ns.FacilityView.prototype, EditableViewMixin);

    var views = {
        "home": {
            "view": ns.FacilityView,
            "extra": ["facility_types", "unit_types"]
        },
        "location": {
            "view": ns.FacilityGeocodingView
        },
        "images": {
            "view": ns.FacilityImageMainView
        },
        "documents": {
            "view": ns.FacilityDocumentsMainView
        },
        "rental": {
            "view": ns.RentalTypesView
        },
        "blocked_time": {
            "view": ns.FacilityBlockedTimeView
        },
        "administrators": {
            "view": ns.FacilityAdministratorView,
            "extra": ["model"]
        },
        "internal_notes": {
            "view": ns.FacilityInternalNotesView
        },
        "calendar": {
            "view": ns.FacilityCalendarView
        }
    };

    ns.FacilityMainView = Backbone.View.extend({

        initialize: function () {
            this.views = {};
            this.setupViews();
            this.router = new Flod.Router(this.model);
            this.router.on("navigate", this.pathChanged, this);
            Backbone.history.start();

            this.facilityHeaderView = new Flod.FacilityHeaderView({
                model: this.model,
                el: "#facilityHeader"
            });
        },

        setupViews: function () {
            this.views = {};
            _.each(views, function (data, id) {
                var options = {
                    "model": this.model,
                    "editable": this.options.editable,
                    "el": $("#" + id)
                };
                if (data.extra) {
                    _.extend(
                        options,
                        _.reduce(data.extra, function (options, key) {
                            options[key] = this.options[key];
                            return options;
                        }, {}, this)
                    );
                }
                var view = new data.view(options);
                view.render();
                if (view.toggleEditable) {
                    view.toggleEditable(this.options.editable);
                }
                this.views[id] = view;
            }, this);

        },

        render: function () {
            this.facilityHeaderView.render();
            return this;
        },

        pathChanged: function (path) {
            if (!views[path].renderImmediately) {
                this.views[path].render();
                if (this.views[path].toggleEditable) {
                    this.views[path].toggleEditable(this.options.editable);
                }
            }
        }
    });

}(Flod));
