var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var ApplicationRow = Backbone.View.extend({

        tagName: "tbody",

        template: $("#appplication_list_element_template").html(),

        events: {
            "click .btn-danger": "destroy"
        },

        initialize: function () {
            _.bindAll(this, "destroy", "destroyed", "error");
        },

        render: function () {

            var times = _.map(this.model.getSlots(), function (slot) {
                return ns.formatSlot(slot, this.model.get('type'));
            }, this);

            var aktor = "Privatlån";
            if (this.model.get("organisation").uri) {
                if (this.model.get("organisation").name) {
                    aktor = this.model.get("organisation").name;
                } else {
                    aktor = 'Ad-hoc aktør';
                }
            }

            var person = "";
            if (this.model.get("person").id) {
                person = this.model.get("person").first_name + ' ' + this.model.get("person").last_name;
            }

            var isDeletable = this.model.canDelete();

            var canClone = ((this.model instanceof RepeatingApplication) && this.model.get("status") === 'Granted' &&
            this.model.get("resource").is_deleted === false && this.model.get("resource").is_published === true);

            var canRelease = (
                (this.model instanceof RepeatingApplication) &&
                this.model.get("status") === 'Granted' &&
                this.model.get("resource").is_deleted === false &&
                this.model.get("resource").is_published === true &&
                this.model.isAfter(moment()));

            var data = {
                "application_id": this.model.get("id"),
                "type": this.model.getType(),
                "status": ns.application_status_map[this.model.get("status")].name,
                "class_name": ns.application_status_map[this.model.get("status")]["class"],
                "resource": this.model.get("resource").name,
                "requested_resource": this.model.get("requested_resource").name,
                "times": times,
                "aktor": aktor,
                "person": person,
                "isDeletable": isDeletable,
                "resource_is_deleted": this.model.get("resource").is_deleted,
                "resource_is_published": this.model.get("resource").is_published,
                "requested_resource_is_deleted": this.model.get("requested_resource").is_deleted,
                "requested_resource_is_published": this.model.get("requested_resource").is_published,
                "canClone": canClone,
                "canRelease": canRelease,
                "id": this.model.get("id"),
                "resource_id": this.model.get("resource").id
            };

            this.$el.html(_.template(this.template, data));
            return this;
        },

        destroy: function () {
            if (this.model.isDeletable) {
                this.modal = new Flod.Modal({
                    "template_data": {
                        "title": "Avbestille",
                        "btn_txt": "Ok",
                        "btn_cancel_txt": "Avbryt"
                    }
                });

                this.modal.render();
                this.modal.$(".modal-body").html("Er du sikker på at du vil si i fra deg/dere denne avtalen?<br>NB: kan ikke angres!");

                this.modal.on("submit", this.deleteApplication, this);
                this.modal.show();

            }
        },

        deleteApplication: function () {
            this.modal.hide();
            this.modal = null;

            this.model.destroy({
                "wait": true,
                "success": this.destroyed,
                "error": this.error
            });
        },

        destroyed: function () {
            this.remove();
        },

        error: function (model, xhr, options) {
            var error = JSON.parse(xhr.responseText);

            if (error['__error___']) {
                var errorString = error["__error__"].join(", ");
            }
            var notifier = new ns.Notifier().render(
                "En feil oppstod:",
                errorString || error.message,
                "error"
            );
            $('#alert').append(notifier.$el);
            notifier.el.scrollIntoView();
            $(".alert").removeClass("offset1");
        }
    });

    ns.ApplicationsListView = Backbone.View.extend({

        initialize: function () {
            var typeChooser = new ApplicationTypeRouter({"el": $(".application-tabs")});
            typeChooser.on("change", this.render, this);
        },

        render: function (type) {
            var applications = new Flod.Applications();
            if (type === "history") {
                applications = new Flod.Applications(this.options.applications.filter(function (application) {
                    return !application.isAfter(moment());
                }));
            } else if (type === "applications") {
                applications = new Flod.Applications(this.options.applications.filter(function (application) {
                    return application.isAfter(moment());
                }));
            } else if (type === "strotimer") {
                applications = new Flod.Applications(this.options.applications.filter(function (application) {
                    return application.get('type') === 'strotime' && application.isAfter(moment());
                }));
            }
            applications = new ApplicationsTableView({"collection": applications}).render();
            this.$("#applications").html(applications.$el);
            return this;
        },

        addAll: function () {
            this.collection.each(this.addOne, this);
        },

        addOne: function (application) {
            this.$el.append(new ApplicationRow({"model": application}).render().$el);
        }
    });

    var ApplicationsTableView = Backbone.View.extend({

        tagName: "table",

        className: "table table-bordered",

        template: $("#appplication_list_header_template").html(),

        render: function () {
            this.$el.append(_.template(this.template));
            this.addAll();
            return this;
        },

        addAll: function () {
            this.collection.each(this.addOne, this);
        },

        addOne: function (application) {
            this.$el.append(new ApplicationRow({"model": application}).render().$el);
        }
    });

    var Application = Backbone.Model.extend({

        isDeletable: false,

        getSlots: function () {
            return _.map(this.get("slots"), function (slot) {
                return _.clone(slot);
            }, this);
        },

        isAfter: function (date) {
            var oks = _.map(this.getSlots(), function (slot) {
                if (slot.end_date) {
                    return moment(slot.end_date, "YYYY-MM-DD").isAfter(date);
                } else {
                    return moment(slot.end_time).isAfter(date);
                }
            });
            return (oks.indexOf(true) !== -1);
        },

        startIsAfter: function (date) {
            var oks = _.map(this.getSlots(), function (slot) {
                if (slot.start_date) {
                    return moment(slot.start_date, "YYYY-MM-DD").isAfter(date);
                } else {
                    return moment(slot.start_time).isAfter(date);
                }
            });
            return (oks.indexOf(true) !== -1);
        },

        canDelete: function () {
            // Cannot delete applications which are explicitly not deletable
            if (!this.isDeletable) {
                return false;
            }

            // Can delete applications that haven't been granted or denied
            var status = this.get("status");
            if (status !== "Granted" && status !== "Denied") {
                return true;
            }

            // Cannot delete past applications
            if (!this.isAfter(moment())) {
                return false;
            }

            // Can delete granted applications if period not started yet
            if (status === "Granted" && this.startIsAfter(moment())) {
                return true;
            }

            return false;
        }
    });

    var RepeatingApplication = Application.extend({
        isDeletable: true,

        url: function () {
            return "/api/booking/v1/applications/" + this.get("id");
        },

        getType: function () {
            return "Fast lån";
        }
    });

    var SingleApplication = Application.extend({
        isDeletable: true,

        url: function () {
            return "/api/booking/v1/applications/" + this.get("id");
        },

        getType: function () {
            return "Engangslån";
        }
    });

    var StroApplication = Application.extend({

        isDeletable: true,

        url: function () {
            return "/api/booking/v1/applications/strotime/" + this.get("id");
        },

        getType: function () {
            return "Strøtime";
        }
    });

    var ApplicationTypeRouter = Backbone.Router.extend({

        initialize: function (options) {
            this.options = options;
        },

        routes: {
            "": "applications",
            "strotimer": "strotimer",
            "history": "history"
        },

        applications: function () {
            this.options.el.find("#applications_tab").tab('show');
            this.trigger("change", "applications");
        },

        strotimer: function () {
            this.options.el.find("#strotime_tab").tab('show');
            this.trigger("change", "strotimer");
        },

        history: function () {
            this.options.el.find("#history_tab").tab('show');
            this.trigger("change", "history");
        }
    });

    ns.Applications = Backbone.Collection.extend({
        model: Application,

        _prepareModel: function (attrs, options) {
            if (attrs instanceof Backbone.Model) {
                if (!attrs.collection) {
                    attrs.collection = this;
                }
                return attrs;
            }
            options || (options = {});
            options.collection = this;

            var modelType = this.model;
            if (attrs.type === 'repeating') {
                modelType = RepeatingApplication;
            } else if (attrs.type === 'single') {
                modelType = SingleApplication;
            } else if (attrs.type === 'strotime') {
                modelType = StroApplication;
            } else {
                return;
            }

            var model = new modelType(attrs, options);
            if (!model._validate(attrs, options)) {
                this.trigger('invalid', this, attrs, options);
                return false;
            }
            return model;
        },

        comparator: function (model) {
            return -moment(model.get("application_time")).valueOf();
        }
    });
}(Flod));
