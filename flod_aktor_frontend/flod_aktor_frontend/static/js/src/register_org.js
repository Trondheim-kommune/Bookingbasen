var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var WarningModal = Flod.Modal.extend({
        template: $('#no_brreg_modal_template').html()
    });

    var TypeChooser = Backbone.View.extend({

        template: $("#type_reg_choose_template").html(),

        events: {
            "change input[name=typeRadio]": "changeType"
        },

        initialize: function () {
            _.bindAll(this, "changeType");
        },

        render: function () {
            this.$el.html(_.template(this.template));
            return this;
        },

        setBrreg: function () {
            console.log("set brreg")
            this.$('#with_brreg').prop('checked', true);
        },

        changeType: function () {
            var type = this.$el.find("input[name=typeRadio]:checked").val();
            if (type === 'no_brreg' && this.options.user_mode !== 'admin') {
                this.modal = new WarningModal({});
                this.modal.render();
                this.modal.on("cancel", this.setBrreg, this);
                this.modal.on("submit", function () {
                    this.modal.$el.modal('hide');
                    this.trigger("changeType", type);
                }, this);
                this.modal.show();
            } else {
                this.trigger("changeType", type);
            }
        }
    });


    var SearchResult = Backbone.Model.extend({
        parse: function (response, options) {
            return _.reduce(response, function (res, value, key) {
                //Handle UTF8-strings
                if (_.isString(value)) {
                    res[key] = decodeURIComponent(escape(value));
                } else {
                    res[key] = value;
                }
                return res;
            }, {});
        }
    });

    var BrregSearchResults = Backbone.Collection.extend({

        url: "/api/organisations/v1/brreg/search",

        model: SearchResult,

        search: function (search_str, callback, error) {
            this.fetch({
                "reset": true,
                "data": {
                    "name": search_str
                },
                "success": callback,
                "error": error
            });
        }
    });

    var SearchResultView = Backbone.View.extend({

        tagName: "li",

        events: {
            "click": "select"
        },

        initialize: function () {
            _.bindAll(this, "select");
        },

        render: function () {

            var link = $("<a href='#'>" + this.model.get("name") + "</a>");
            if (this.model.get("is_registered")) {
                link.append('<i class="icon-pencil pull-right"></i>');
                this.$el.attr("title", "Aktøren er allerede registrert i Aktørbasen.");
            } else {
                link.append('<i class="icon-plus pull-right"></i>');
                this.$el.attr("title", "Trykk for å laste inn informasjon fra Brønnøysundregistrene til Aktørbasen. Deretter kan du redigere informasjon om aktøren.");
            }
            this.$el.html(link);
            return this;
        },

        select: function () {
            this.model.collection.trigger("selected", this.model);
        }
    });

    var SearchResultsView = Backbone.View.extend({

        tagName: "ul",

        className: "nav nav-tabs nav-stacked searchresults",

        render: function () {
            this.$el.html();
            this.collection.each(function (model) {
                this.$el.append(new SearchResultView({"model": model}).render().$el);
            }, this);
            return this;
        }
    });

    var BrregInfoView = Backbone.View.extend({

        className: "well",

        template: $("#brreg_information_template").html(),

        render: function () {
            this.$el.html(_.template(this.template, this.model.toDisplay()));
            return this;
        }
    });

    var BrregSearchView = Backbone.View.extend({

        template: $("#brreg_search_template").html(),

        events: {
            "click #search_org": "searchOrg"
        },

        initialize: function () {
            _.bindAll(this, "searchOrg", "foundOrganisations", "foundOrganisation", "searchError");
            this.searchResults = new BrregSearchResults();
            this.searchResults.on("selected", this.selectedOrganisation, this);
        },

        render: function () {
            this.$el.html(_.template(this.template));
            return this;
        },

        searchOrg: function () {
            this.$(".alert").remove();
            var search_str = this.$("#org_nr").val();
            if (search_str !== "") {
                this.$(".org_search_results").html("");
                this.trigger("reset");
                this.$(".searchresults").remove();
                this.$(".org_search_results").addClass("searching");
                if (!isNaN(search_str)) {
                    this.getByOrgNr(search_str);
                } else {
                    this.searchResults.search(search_str, this.foundOrganisations, this.searchError);
                }
            }
        },

        selectedOrganisation: function (organisation) {

            if (organisation.has("id")) {
                window.location = "/organisations/" + organisation.get("id");
            } else {
                this.$(".searchresults").remove();
                this.getByOrgNr(organisation.get("org_number"));
            }
        },

        getByOrgNr: function (orgNr) {
            this.$(".org_search_results").addClass("searching");
            this.result = new ns.BrregOrganisation({"org_number": orgNr});
            this.result.fetch({"success": this.foundOrganisation, "error": this.searchError});
        },

        foundOrganisations: function (organisations) {
            this.$(".org_search_results").removeClass("searching");
            if (organisations.length) {
                this.$(".org_search_results").append(new SearchResultsView({"collection": organisations}).render().$el);
            } else {
                this.$(".org_search_results").append($("<div class='alert push--top'>Fant ingen organisasjoner i Brreg!</div>"));
            }
        },

        foundOrganisation: function (organisation) {
            this.$(".org_search_results").removeClass("searching");
            this.model = new ns.Organisation(organisation.attributes);
            this.$(".org_search_results").append(
                new BrregInfoView({"model": this.model}).render().$el
            );
            this.trigger("found_org");
        },

        searchError: function (model, response) {
            this.$(".org_search_results").removeClass("searching");
            var responseText = $.parseJSON(response.responseText);
            var errorString = responseText["__error__"].join(", ");
            this.$(".org_search_results").append($("<div class='alert push--top'>" + errorString + "</div>"));
        }
    });

    ns.fixUrl = function (url) {
        if (url.substring(0, "http".length) === "http") {
            return url;
        }
        return "http://" + url;
    };

    ns.RegisterOrgView = Backbone.View.extend({

        initialize: function () {
            this.typeChooser = new TypeChooser({"el": this.$("#type_add"), "user_mode": this.options.user_mode});
            this.typeChooser.on("changeType", this.changeType, this);

            this.brregSearchView = new BrregSearchView();
            this.brregSearchView.on("found_org", this.showOrgInfoForm, this);
            this.brregSearchView.on("reset", this.resetData, this);
            this.changeType("with_brreg");
        },

        render: function () {
            this.typeChooser.render();
            return this;
        },

        changeType: function (type) {
            this.resetData();
            if (type === "no_brreg") {
                this.$("#type_field").hide();
                var org = new ns.Organisation();
                this.showOrgInfoForm(org);

            } else {
                this.$("#type_field").show();
                this.brregSearchView.setElement(this.$("#type_field"));
                this.brregSearchView.render();
            }
        },

        resetData: function () {
            if (this.organisationInfoForm) {
                this.organisationInfoForm.clear();
            }
        },

        showOrgInfoForm: function (model) {
            model = model || this.brregSearchView.model;

            if (this.organisationInfoForm) {
                this.organisationInfoForm.undelegateEvents();
            }

            this.organisationInfoForm = new ns.OrganisationInfoFormView({
                "el": this.$("#extra_info"),
                "model": model,
                "districts": this.options.districts,
                "recruiting_districts": this.options.recruiting_districts,
                "brreg_activity_codes": this.options.brreg_activity_codes,
                "user_mode": this.options.user_mode
            });
            this.organisationInfoForm.showDelete = false;
            this.organisationInfoForm.render();

            this.organisationInfoForm.saveCallback = function (organisation) {
                window.location = "/organisations/" + organisation.get("id");
            };
        }
    });


}(Flod));
