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

    _.extend(ns.UmbrellaInformationView.prototype, EditableViewMixin);
    _.extend(ns.MemberOrganisationsView.prototype, EditableViewMixin);
    _.extend(ns.ResponsiblePersonsView.prototype, EditableViewMixin);

    var views = {
        "home": {
            "view": ns.UmbrellaInformationView
        },
        "member_organisations": {
            "view": ns.MemberOrganisationsView
        },
        "responsible_persons": {
            "view": ns.ResponsiblePersonsView
        }
    };

    ns.UmbrellaMainView = Backbone.View.extend({

        initialize: function () {
            this.views = {};
            this.setupViews();
            this.router = new Flod.Router(this.model);
            this.router.on("navigate", this.pathChanged, this);
            Backbone.history.start();

            this.umbrellaOrganisationHeaderView = new Flod.UmbrellaOrganisationHeaderView({
                model: this.model,
                el: "#umbrellaOrganisationTab"
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
                if (!data.delayRender) {
                    view.render();
                }
                if (view.toggleEditable) {
                    view.toggleEditable(this.options.editable);
                }
                this.views[id] = view;
            }, this);

        },

        render: function () {
            this.umbrellaOrganisationHeaderView.render();
            return this;
        },

        pathChanged: function (path) {
            if (!views[path].renderImmediately) {
                if (this.views[path].toggleEditable) {
                    this.views[path].toggleEditable(this.options.editable);
                }
            }
        }
    });

}(Flod));