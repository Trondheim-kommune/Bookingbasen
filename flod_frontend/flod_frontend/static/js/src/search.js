var Flod = Flod || {};
(function (ns) {
    "use strict";

    var greenIcon = L.icon({
        iconUrl: L.Icon.Default.imagePath + '/marker-icon-green.png',
        shadowUrl: L.Icon.Default.imagePath + '/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    var SearchResult = SpatialBB.MarkerModel.extend({

        defaults: {
            "selected": false
        },

        parse: function (response) {
            response = SpatialBB.MarkerModel.prototype.parse.apply(this, arguments);
            if (!response.image) {
                response.image = false;
            }
            if (!response.description) {
                response.description = "N/A";
            }
            return response;
        },

        initialize: function () {
            SpatialBB.MarkerModel.prototype.initialize.apply(this, arguments);
            _.bindAll(this, "highlightMarker", "deHighlightMarker");
        },

        createMarker: function (position) {
            if (position) {
                this.marker = new L.Marker(
                    [position.lat, position.lon],
                    {title: this.get('name')}
                );
                this.marker.on('click', this.markerClicked, this);
            }
        },

        highlightMarker: function () {
            if (this.marker && this.collection.hasMap) {
                // this.marker.setIcon(greenIcon);
                // Setting icon src manually to bypass bug in leaflet (https://github.com/Leaflet/Leaflet/issues/561). Cannot upgrade leaflet without fixing SpatialBB as well.
                this.marker._icon.src = greenIcon.options.iconUrl;
                this.marker.setZIndexOffset(1000);

            }
        },
        deHighlightMarker: function () {
            if (this.marker && this.collection.hasMap) {
                // this.marker.setIcon(new L.Icon.Default());
                // Setting icon src manually to bypass bug in leaflet (https://github.com/Leaflet/Leaflet/issues/561). Cannot upgrade leaflet without fixing SpatialBB as well.
                this.marker._icon.src = (new L.Icon.Default())._getIconUrl("icon");
                this.marker.setZIndexOffset(0);

            }
        },

        markerClicked: function () {
            var date = "";
            if (this.collection.params.date) {
                date = "#date" + moment(this.collection.params.date).format();
            }
            window.location = "/facilities/" + this.get("id") + date;
        }
    });

    var toUrlParams = function (params) {

        return _.map(params, function (value, key) {
            return key + "=" + encodeURIComponent(value);
        }).join("&");
    };

    var SearchResults = ns.SearchResults = SpatialBB.MarkerCollection.extend({

        baseUrl: "/api/facilities/v1/facilities/",

        model: SearchResult,

        requirePosition: false,

        url: function () {
            var url = this.baseUrl;
            if (this.params) {
                url += "?" + toUrlParams(this.params);
            }
            return url;
        },

        setParams: function (params) {
            this.params = params;
        },

        getSelected: function () {
            return this.filter(function (result) {
                return result.get("selected");
            });
        }
    });

    ns.SearchView = Backbone.Router.extend({

        initialize: function (options) {
            this.options = options;
        },

        routes: {
            "(category=:category)": "search",
            "map(/category=:category)": "mapsearch"
        },

        search: function (category) {
            this.options.el.find("#search_tab").tab('show');
            new SearchView({
                "el": this.options.el.find(".search_content"),
                "data": this.options.data,
                "category": category
            }).render();
        },

        mapsearch: function (category) {
            this.options.el.find("#map_search_tab").tab('show');
            new MapSearchView({
                "el": this.options.el.find(".search_content"),
                "data": this.options.data,
                "category": category
            }).render();
        }
    });

    var ResultView = Backbone.View.extend({

        className: "row-fluid searchresult",

        template: $("#search_result_template").html(),

        events: {
            "click .details": "showFacility",
            "click .booking": "bookFacility",
            "mouseenter": "highlight",
            "mouseleave": "dehighlight",
            "change #select_result": "selectResult"
        },

        initialize: function () {
            _.bindAll(this, "showFacility", "highlight",
                "dehighlight", "selectResult", "bookFacility");
            var marker = this.model.getMarker();
            if (marker) {
                marker.on("mouseover", this.highlight, this);
                marker.on("mouseout", this.dehighlight, this);
            }
        },

        render: function () {
            var data = this.model.toJSON();

            if (this.model.get("images").length) {
                data.image = new ns.Image(this.model.get("images")[0]).getImageUrl(200, 150);
            }
            this.$el.html(_.template(this.template, data));
            return this;
        },

        showFacility: function () {
            var date = "";
            if (this.model.collection.params.date) {
                date = "#date" + moment(this.model.collection.params.date).format();
            }
            //possibly show in a modal or something more fancy? works for now..
            window.location = "/facilities/" + this.model.get("id") + date;
        },

        highlight: function () {
            this.$el.addClass("highlight");
            this.model.highlightMarker();
        },

        dehighlight: function () {
            this.$el.removeClass("highlight");
            this.model.deHighlightMarker();
        },

        selectResult: function (e) {
            this.model.set({"selected": $(e.currentTarget).is(':checked')});
        },

        bookFacility: function () {
            window.location = "/booking/" + this.model.get("id");
        }
    });

    var PaginationView = Backbone.View.extend({

        template: $("#pagination_template").html(),

        className: "row-fluid searchresult",

        events: {
            "click .prev": "goBack",
            "click .next": "goForward"
        },

        initialize: function () {
            _.bindAll(this, "goBack", "goForward");
        },

        render: function (numElements, numPrPage, offset) {
            this.$el.html("");

            var prev = false, next = false;
            var numPages = Math.ceil(numElements / numPrPage);
            var currentPage = (offset / numPrPage) + 1;

            if (currentPage > 1) {
                this.prevOffset = offset - numPrPage;
                prev = true;
            }
            if (currentPage < numPages) {
                this.nextOffset = offset + numPrPage;
                next = true;
            }

            this.$el.append(_.template(this.template, {
                prev: prev,
                next: next,
                numPrPage: numPrPage
            }));
            return this;
        },

        goBack: function () {
            this.trigger("changePage", this.prevOffset);
        },

        goForward: function () {
            this.trigger("changePage", this.nextOffset);
        }
    });

    var ResultsView = Backbone.View.extend({

        template: $("#seach_result_top_template").html(),

        notFoundTemplate: $("#notfound_template").html(),

        searchingTemplate: $("#searching_template").html(),

        resultsPrPage: 10,

        offset: 0,

        events: {
            "click #show_times": "showTimeForSelected",
            "click #show10": "show10",
            "click #show20": "show20",
            "click #show50": "show50"
        },

        initialize: function () {
            _.bindAll(this, "showTimeForSelected", "show10", "show20", "show50");
            this.collection.on("reset", this.render, this);
            this.collection.on("change:selected", this.toggleTimeButton, this);
            this.collection.on("startSearch", this.startSearch, this);
            this.paginationView = new PaginationView();
            this.paginationView.on("changePage", this.changePage, this);
        },

        show10: function () {
            this.changeNum(10);
            return false;
        },

        show20: function () {
            this.changeNum(20);
            return false;
        },

        show50: function () {
            this.changeNum(50);
            return false;
        },

        startSearch: function () {
            this.paginationView.remove();
            this.$el.html("");
            this.$el.html(_.template(this.searchingTemplate));
            this.offset = 0;
        },

        render: function () {
            this.paginationView.remove();
            this.$el.html("");
            if (this.collection.length) {
                var resultsSelected = (this.collection.getSelected().length > 0);
                this.$el.html(_.template(this.template, {
                    "num_results": this.collection.length,
                    "resultsSelected": resultsSelected,
                    "resultsPrPage": this.resultsPrPage,
                    "numResults": this.collection.length
                }));
            } else {
                this.$el.html(_.template(this.notFoundTemplate));
            }

            var res = _.map(this.collection.slice(this.offset, this.offset + this.resultsPrPage), function (result, nr) {
                return new ResultView({"model": result}).render().$el;
            });
            this.$el.append(res);
            if (this.collection.length > this.resultsPrPage) {
                this.$el.append(this.paginationView.render(
                    this.collection.length,
                    this.resultsPrPage,
                    this.offset
                ).$el);
                this.paginationView.delegateEvents();
            }
        },

        changeNum: function (resultsPrPage) {
            this.resultsPrPage = resultsPrPage;
            this.render();
        },

        changePage: function (offset) {
            this.offset = offset;
            this.render();
        },

        showTimeForSelected: function () {
            var selected = this.collection.getSelected();
        },

        toggleTimeButton: function () {
            if (this.collection.getSelected().length) {
                this.$("#show_times").removeAttr("disabled");
            } else {
                this.$("#show_times").attr("disabled", "disabled");
            }
        }
    });

    var SearchMixin = {
        search: function (params) {
            if (params.district === "0") {
                delete params.district;
            }

            this.collection.setParams(params);
            this.collection.trigger("startSearch");
            this.collection.fetch({reset: true});
        }
    };

    var SearchView = Backbone.View.extend({

        template: $("#search_template").html(),

        initialize: function () {
            this.collection = new SearchResults();
            this.collection.hasMap = false;
            this.filterView = new FilterSearchView({
                "data": this.options.data,
                "collection": this.collection,
                "category": this.options.category
            });

            this.filterView.on("search", this.search, this);
            this.resultsView = new ResultsView({
                "collection": this.collection
            });
        },

        render: function () {
            this.$el.html(_.template(this.template));
            this.filterView.setElement(this.$("#search_params"));
            this.filterView.render();
            this.resultsView.setElement(this.$("#search_results"));
            return this;
        }
    });

    _.extend(SearchView.prototype, SearchMixin);

    var MapSearchView = SearchView.extend({

        template: $("#map_search_template").html(),

        initialize: function () {
            SearchView.prototype.initialize.apply(this, arguments);
            this.mapView = new Flod.SearchMapView(
                {"collection": this.collection}
            );
            this.filterView.on(
                "changeBbox",
                this.mapView.zoomToBounds,
                this.mapView
            );
            this.collection.hasMap = true;
        },

        render: function () {
            SearchView.prototype.render.apply(this, arguments);
            this.mapView.setElement(this.$("#map"));
            this.mapView.render();
            return this;
        }
    });

    _.extend(MapSearchView.prototype, SearchMixin);

    function fixDistricts(districts) {
        var bounds = _.reduce(districts, function (bounds, district) {
            bounds.extend(new L.GeoJSON(district.geometry).getBounds());
            return bounds;
        }, new L.LatLngBounds());

        var whole = new L.Polygon([
            bounds.getSouthWest(),
            bounds.getNorthWest(),
            bounds.getNorthEast(),
            bounds.getSouthEast()
        ]);

        var fixed = _.map(districts, function (district) {
            var cloned = _.clone(district);
            cloned.geometry = L.GeoJSON.geometryToLayer(cloned.geometry);
            return cloned;
        });

        fixed.unshift({"name": "Hele Trondheim", "geometry": whole});

        return fixed;
    }

    var FilterSearchView = Backbone.View.extend({

        formElements: [
            {
                "name": "type",
                "type": Flod.FormElems.FormSelect,
                "data": {"id": "type", "label": "Type rom/lokale", "options": {"0": {"name": "Lokale"}, "1": {"name": "Idrettsarena"}}}
            },
            {
                "name": "size",
                "type": Flod.FormElems.MinMaxSelect,
                "data": {
                    "id": "capacity", "label": "Størrelse (antall personer)", "options": [
                        {"name": "---"},
                        {"name": "0-50 personer", "min": 0, "max": 50},
                        {"name": "50-150 personer", "min": 50, "max": 150},
                        {"name": "150-250 personer", "min": 150, "max": 250},
                        {"name": "250-500 personer", "min": 250, "max": 500},
                        {"name": "500+ personer", "min": 500}
                    ]
                }
            },
            {
                "name": "district",
                "type": Flod.FormElems.FormBboxSelect,
                "data": {"id": "district", "label": "Bydel", "options": []}
            },
            /*
             kommentert bort pga feilen som må fikses først, da denne dd fungerer ikke
             {
             "name": "activity_type",
             "type":  Flod.FormElems.FormSelect,
             "data": {"id": "activity_type", "label": "Aktivitetstype", "options":
             {
             "0": {"name": "Dans"},
             "1": {"name": "Filmvisning"},
             "2": {"name": "Formingsaktivitet, hobby"},
             "3": {"name": "Idrett, trening"},
             "4": {"name": "Kor"},
             "5": {"name": "Korps, orkester"},
             "6": {"name": "Kurs, undervisning"},
             "7": {"name": "Utstilling"},
             "8": {"name": "Konsert, forestilling, drama"},
             "9": {"name": "Møte, konferanse, seminar"}
             }
             }
             },*/
            {
                "name": "accessibility",
                "type": Flod.FormElems.CheckBoxGroup,
                "data": {
                    "id": "accessibility",
                    "label": "Spesielle behov",
                    "checkboxes": [
                        {"id": "elevator", "name": "Heis"},
                        {"id": "marking_for_visually_impaired", "name": "Tilrettelagt for svaksynte"},
                        {"id": "induction_loop", "name": "Teleslynge"},
                        {"id": "available_by_wheelchair", "name": "Tilrettelagt for rullestolbrukere"},
                        {"id": "wheelchair_wc", "name": "Toalett for rullestolbrukere"}
                    ]
                }
            }
        ],

        events: {
            "click .search": "doSearch",
            'click [type="checkbox"]': 'doSearch',
            "change #type, #district, #capacity, #activity_type": "doSearch"
        },

        initialize: function () {
            _.bindAll(this, "doSearch");

            _.find(this.formElements, function (element) {
                return (element.name === "district");
            }).data.options = fixDistricts(this.options.data.districts);

            if (this.options.category && this.options.data.facility_types[this.options.category]) {
                this.options.data.facility_types[this.options.category].selected = true;
            }

            _.find(this.formElements, function (element) {
                return (element.name === "type");
            }).data.options = _.clone(this.options.data.facility_types);

            this.elements = _.map(this.formElements, function (formElement) {
                var element = new formElement.type(formElement.data).render();
                if (element instanceof Flod.FormElems.FormBboxSelect) {
                    element.on("change", this.bboxSelected, this);
                }
                return element;
            }, this);
        },

        render: function () {
            this.$el.html("");
            this.$el.append(_.pluck(this.elements, "$el"));
            this.$el.append(_.template($("#search_button_template").html()));
            return this;
        },

        doSearch: function () {
            var extractParams = function (params, element) {
                var value = element.getValue();
                if (value !== null && value !== "") {
                    if (_.isObject(value)) {
                        _.each(value, function (val, key) {
                            if (val) {
                                params[key] = val;
                            }
                        });
                    } else {
                        params[element.id] = value;
                    }
                }
                return params;
            };

            // Extract parameters for all fields except the accessibility checkboxes
            var elementsExceptAccessibility = _.filter(this.elements, function (element) {
                return element.id !== "accessibility";
            });

            var params = _.reduce(elementsExceptAccessibility, extractParams, {});

            // Extract the accessibility checkboxes..
            var accessibilityCheckboxes = _.filter(this.elements, function (element) {
                return element.id === "accessibility";
            });

            // and make as comma-separated string
            var accessibilityKeys = _.keys(_.reduce(accessibilityCheckboxes, extractParams, {}));
            if (!_.isEmpty(accessibilityKeys)) {
                params.accessibility = accessibilityKeys.join(",");
            }
            if (params.bbox) {
                delete params.bbox;
            }

            this.trigger("search", params);
        },

        bboxSelected: function (selected) {
            this.deselectBboxDropdowns(selected);
            this.trigger("changeBbox", selected.bbox.bbox);
        },

        deselectBboxDropdowns: function (except) {
            var deselect = _.filter(this.elements, function (element) {
                return (element instanceof Flod.FormElems.FormBboxSelect);
            });
            if (except) {
                deselect = _.filter(deselect, function (element) {
                    return (element.id !== except.id);
                });
            }
            _.each(deselect, function (element) {
                element.selectOption(0);
            });
        }
    });
}(Flod));
