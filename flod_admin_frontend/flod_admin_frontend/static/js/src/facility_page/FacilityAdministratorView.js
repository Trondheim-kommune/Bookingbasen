var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.UserCollection = Backbone.Collection.extend({

        baseUrl: "/api/users/v1/users/",

        filters: {},

        initialize: function (model, options) {
            if (options && options.filters) {
                this.filters = options.filters;
            }
        },

        /**
         *
         * @param filters   filter object, each key-value represents a filter that will be attached to GET URL
         */
        setFilters : function (filters) {
            this.filters = filters;
        },

        hasStaticParameters: function () {
            return (Object.keys(this.filters).length > 0);
        },

        createParamsListForUrl: function () {
            return _.map(this.filters, function (value, key) {
                return encodeURIComponent(key) + "=" + encodeURIComponent(value);
            }).join("&");
        },

        url: function () {
            var url = this.baseUrl;
            if (this.hasStaticParameters()) {
                url = url + "?" + this.createParamsListForUrl();
            }
            return url;
        }

    });

    ns.FacilityAdministratorView = Backbone.View.extend({

        initialize: function () {

            var facility_id = null;
            if (this.options.model && this.options.model.get('id')) {
                facility_id = this.options.model.get('id');
            }

            var administratorsCollection = new ns.UserCollection();
            var currentFacilityAdministratorsView = new Flod.UserCollectionView({
                editable: this.options.editable,
                el : this.$('#current_admins_list'),
                collection: administratorsCollection,
                facility_id: facility_id
            });

            var addCredentialToUserView = new Flod.AddCredentialToUserView({
                editable: this.options.editable,
                facility : this.model,
                currentAdminCollection: administratorsCollection,
                el: this.$('#add_admin_credential')
            });
            new Flod.QuickSearch({
                el: this.$("#add_admin_credential_form"),
                typeAheadInputField: this.$("#bruker_private_id"),
                dropdownMenu: this.$("#quick_search_results"),
                resultTemplate: $("#admin_result_template").html(),
                baseUrl: "/api/users/v1/users/",
                staticParams: {
                    authentication_type: "active_directory"
                },
                dynamicParams: {
                    private_id_starting_with: "#bruker_private_id"
                },
                assignSelectedObject : addCredentialToUserView
            }).render();
        }
    });

}(Flod));