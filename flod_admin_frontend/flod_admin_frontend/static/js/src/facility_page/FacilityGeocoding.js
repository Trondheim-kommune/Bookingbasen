/*global L: false, Backbone:false, SpatialBB:false*/
var Flod = this.Flod || {};

(function (ns, undefined) {
    "use strict";

    L.Icon.Default.imagePath = "/static/js/lib/leaflet/images";

    var grayIcon = L.icon({
        iconUrl: L.Icon.Default.imagePath + '/marker-icon-gray.png',
        iconRetinaUrl: L.Icon.Default.imagePath + '/marker-icon-gray@2x.png',
        shadowUrl: L.Icon.Default.imagePath + '/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    var Building = SpatialBB.MarkerModel.extend({

        initialize: function () {
            SpatialBB.MarkerModel.prototype.initialize.apply(this, arguments);
            this.marker.on("click", _.bind(this.clickMarker, this));
            if (this.get("selected")) {
                this.setSelectedIcon();
            } else {
                this.setDeselectIcon();
            }
            this.on("change:selected", this.toggleSelected, this);
        },

        clickMarker: function () {
            this.set("selected", true);
        },

        toggleSelected: function () {
            if (this.get("selected")) {
                this.setSelectedIcon();
            } else {
                this.deselect();
            }
        },

        deselect: function () {
            this.setDeselectIcon();
            this.set({"selected": false}, {"silent": true});
        },

        setSelectedIcon: function () {
            this.marker.setIcon(new L.Icon.Default());
            this.marker.setZIndexOffset(1000);
        },

        setDeselectIcon: function () {
            this.marker.setIcon(grayIcon);
            this.marker.setZIndexOffset(0);
        }
    });

    var BuildingCollection = SpatialBB.MarkerCollection.extend({

        model: Building,

        url: "/api/matrikkel/v1/buildings",

        initialize: function () {
            SpatialBB.MarkerCollection.prototype.initialize.apply(this, arguments);
            this.on("change:selected", this.toggleSelected, this);
            this.on("reset", this.checkResults, this);
        },

        toggleSelected: function (selected) {
            this.each(function (building) {
                if (building.cid !== selected.cid) {
                    building.deselect();
                }
            });
        },

        checkResults: function () {
            if (this.length === 1) {
                this.at(0).set("selected", true);
            }
        },

        search: function (gardsnr, bruksnr, festenr, seksjonsnr, errorCallback) {
            this.trigger("search");
            this.fetch({
                "reset": true,
                "error": errorCallback,
                "data": {
                    "gardsnr": gardsnr,
                    "bruksnr": bruksnr,
                    "festenr": festenr,
                    "seksjonsnr":  seksjonsnr
                }
            });
        }
    });


    var bbox = [63.3027194635967, 10.0035271253386, 63.5165948113832, 10.725167529414];

    var maxBounds = new L.LatLngBounds(
        new L.LatLng(bbox[0], bbox[1]),
        new L.LatLng(bbox[2], bbox[3])
    );

    function createMapWithStandardLayer(element) {

        var map = L.map(
            element,
            {"maxBounds": maxBounds}
        );

        L.tileLayer('http://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=norges_grunnkart&zoom={z}&x={x}&y={y}', {
            attribution: '&copy; Kartverket'
        }).addTo(map);

        return map;
    }


    var MapView = Backbone.View.extend({

        initialize: function (options) {
            _.bindAll(this, "searchError");
            this.addressSearchCollection = options.addressSearchCollection;
            this.addressSearchCollection.on('select', this.addressSelected, this);
            this.addressSearchCollection.on('notfound', this.notfound, this);

            this.buildingCollection = options.buildingCollection;
            this.buildingCollection.on("sync", this.buildingsFound, this);
            this.buildingCollection.on("select", this.buildingSelected, this);
            this.buildingCollection.on("change:selected", this.buildingClick, this);
        },

        render: function () {
            this.map = createMapWithStandardLayer(this.$('.map')[0]);
            if (this.buildingCollection.length) {
                this.zoomToCollection();
            } else {
                this.zoomMax();
            }

            this.map.addLayer(this.buildingCollection.getLayerGroup());
            return this;
        },

        addressSelected: function (address) {
            var matrikkel_ident = address.get("matrikkel_ident");
            this.buildingCollection.search(
                matrikkel_ident.gardsnr,
                matrikkel_ident.bruksnr,
                matrikkel_ident.festenr,
                matrikkel_ident.seksjonsnr,
                this.searchError
            );
        },

        showMarker: function (position) {
            this.buildingCollection.reset();
            this.buildingCollection.add({
                "position": position,
                "selected": true
            });
            this.buildingClick();
        },

        notfound: function () {
            this.map.on("click", _.bind(this.mapClick, this));
            this.$('.map').addClass('normalmarker');
        },

        buildingClick: function () {
            var selected = this.buildingCollection.find(function (model) {
                return model.get("selected");
            });
            this.buildingSelected(selected);
        },

        buildingsFound: function () {
            if (!this.buildingCollection.length) {
                return;
            }
            this.disableClick();
            this.zoomToCollection();
            if (this.buildingCollection.length === 1) {
                this.buildingSelected(this.buildingCollection.at(0));
            } else {
                this.$('#choose_building').removeClass('hidden');
            }
        },

        mapClick: function (evt) {
            this.showMarker({"lat": evt.latlng.lat, "lon": evt.latlng.lng});
        },

        disableClick: function () {
            this.map.off("click");
            this.$('.map').removeClass('normalmarker');
        },

        zoomToCollection: function () {
            var positions = this.buildingCollection.map(function (point) {
                    return point.getMarker().getLatLng();
                });
            this.map.fitBounds(L.latLngBounds(positions));
        },

        zoomMax: function () {
            this.map.fitBounds(maxBounds);
        },

        buildingSelected: function (building) {
            this.$('#choose_building').addClass('hidden');
            this.buildingCollection.trigger("selectedBuilding", building);
        },

        searchError: function () {
            this.buildingCollection.trigger("searchError");
        }

    });


    var AddressSearchResultView = Backbone.View.extend({

        tagName: "li",

        events: {
            "click a": "select"
        },

        initialize: function () {
            _.bindAll(this, "select");
        },

        render: function () {
            this.$el.html($("<a href='#'>" + this.model.get("name") + "</a>"));
            return this;
        },

        select: function () {
            this.model.collection.trigger("select", this.model);
            return false;
        }

    });


    var AddressSearchResultsView = Backbone.View.extend({

        tagName: "div",

        initialize: function () {
            this.collection.on("reset", this.render, this);
        },

        render: function () {
            this.$el.css("position", "relative");
            var list = $("<ul class='nav nav-tabs nav-stacked white-background floating-list''></ul>");
            if (!this.collection.length) {
                this.$el.hide();
            } else {
                this.$el.show();

                this.collection.each(function (result) {
                    list.append(new AddressSearchResultView({"model": result}).render().$el);
                }, this);
            }
            this.$el.html(list);
            return this;
        }

    });



    var AddressSearchCollection = Backbone.Collection.extend({

        url: "/api/matrikkel/v1/addresses",

        search: function (search_str, errorCallback) {
            this.fetch({
                "reset": true,
                "data": {
                    "query": search_str
                },
                "error": errorCallback
            });
        }
    });


    var AddressSearchView = Backbone.View.extend({

        template: $("#facility_geocoding_address_template").html(),

        events: {
            "submit": "search"
        },

        searching: false,

        initialize: function () {
            _.bindAll(this, "search", "searcherror");
            this.collection.on("select", this.selected, this);
            this.collection.on("reset", this.foundResults, this);
            this.addressSearchResultsView = new AddressSearchResultsView({
                "collection": this.collection
            });
            this.address = null;
        },

        render: function () {
            this.$el.html(_.template(this.template));
            this.$("input").after(this.addressSearchResultsView.render().$el);
            if (this.address) {
                this.setSearchTerm(this.address);
            }
            return this;
        },

        search: function () {
            this.$("#nohits").addClass('hidden');
            var val = this.$("#facility_address").val();
            this.trigger("searching");
            this.showSpinner();
            this.collection.search(val, this.searcherror);
            return false;
        },

        showSpinner: function () {
            var el = $("<div>Søker</div>").addClass("searching");
            this.$("button").after(el);
            this.$("button").hide();
        },

        hideSpinner: function () {
            this.$(".searching").remove();
            this.$("button").show();
        },

        selected: function (result) {
            this.setSearchTerm(result.get("name"));
            this.collection.reset([], {silent: true});
            this.addressSearchResultsView.render();
        },

        setSearchTerm: function (name, doSearch) {
            this.$("input").val(name);
            this.address = name;
            if (doSearch) {
                this.showSpinner();
                this.collection.search(name);
            }
        },

        searcherror: function () {
            this.hideSpinner();
            this.collection.trigger("searchError");
        },

        foundResults: function () {
            this.$(".searching").remove();
            if (!this.collection.length) {
                this.showNotFoundError();
                this.collection.trigger("notfound");
            } else if (this.collection.length === 1) {
                this.collection.trigger("select", this.collection.at(0));
            }
        },

        showNotFoundError: function () {
            this.setSearchTerm(null);
            this.hideSpinner();
            this.$("#nohits").removeClass('hidden');
            this.trigger("noSearchResultsFound");
        }
    });


    ns.FacilityGeocodingView = Backbone.View.extend({

        className: "well",

        events: {
            'click #select': 'saveBuilding'
        },

        template: $('#facility_geocoding_template').html(),

        initialize: function (options) {
            _.bindAll(this, "saved");

            this.editable = true;

            this.searchCollection = new AddressSearchCollection();
            this.addressSearchView = new AddressSearchView({
                "collection": this.searchCollection
            });

            this.buildingCollection = new BuildingCollection();
            this.buildingCollection.on('search', this.searchBuilding, this);
            this.buildingCollection.on("sync", this.buildingsFound, this);
            this.buildingCollection.on('selectedBuilding', this.selectedBuilding, this);

            this.mapView = new MapView({
                "addressSearchCollection": this.searchCollection,
                "buildingCollection": this.buildingCollection
            });

            this.addressSearchView.on("searching", this.startSearch, this);
            this.searchCollection.on('searchError', this.searchError, this);
            this.buildingCollection.on('searchError', this.searchError, this);

            if (options) {
                if (!_.isNull(options.editable) && !_.isUndefined(options.editable)) {
                    this.editable = options.editable;
                }
            }
        },

        render: function () {
            this.$el.html(_.template(this.template)({editable: this.editable}));
            if (!this.editable) {
                return this;
            }

            this.addressSearchView.setElement(this.$('#search_form'));
            this.addressSearchView.render();

            this.mapView.setElement(this.$('#map_div'));
            this.mapView.render();
            if (this.model.has("address")) {
                this.addressSearchView.setSearchTerm(
                    this.model.get("address"),
                    !this.model.has("position")
                );
            }
            if (this.model.has("position")) {
                this.mapView.showMarker(this.model.get("position"));
                this.mapView.zoomToCollection();
            }

            return this;
        },

        selectedBuilding: function (building) {
            if (building) {
                this.building = building;
                this.$('#save_position').removeClass('hidden');
            }
        },

        searchError: function () {
            this.$('#search_error').removeClass('hidden');
        },

        startSearch: function () {
            this.$('#save_position').addClass('hidden');
            this.mapView.zoomMax();
            this.buildingCollection.reset([]);
            this.$('#search_error').addClass('hidden');
        },

        searchBuilding: function () {
            this.addressSearchView.showSpinner();
        },

        buildingsFound: function () {
            this.addressSearchView.hideSpinner();
        },

        saveBuilding: function () {
            this.model.set("address", this.addressSearchView.address);
            this.model.set("position", this.building.get("position"));
            this.model.set("building_number", this.building.get("building_number"));
            this.model.save({}, {"success": this.saved});
        },

        saved: function () {
            this.addressSearchView.$("#nohits").addClass('hidden');
            this.mapView.disableClick();
            this.$('#save_position').addClass('hidden');
            this.$el.append(
                new ns.Notifier().render("Posisjonen ble lagret", "", "success", 5, _.bind(function () {
                    this.render();
                }, this)).$el
            );
        }
    });

}(Flod));
