
var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var defaultBounds = [63.3027194635967, 10.0035271253386, 63.5165948113832, 10.725167529414];

    L.Icon.Default.imagePath = "/static/js/lib/leaflet/images";

    function createMapWithStandardLayer(element, bbox) {

        bbox = bbox || defaultBounds;

        var bounds = new L.LatLngBounds(
            new L.LatLng(bbox[0], bbox[1]),
            new L.LatLng(bbox[2], bbox[3])
        );
        var map = L.map(
            element,
            {"maxBounds": bounds}
        ).fitBounds(bounds);

        L.tileLayer('http://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=norges_grunnkart&zoom={z}&x={x}&y={y}', {
            attribution: '&copy; Kartverket'
        }).addTo(map);

        return map;
    }

    ns.SinglePointMapView = Backbone.View.extend({

        render: function () {
            this.map = createMapWithStandardLayer(this.$el.attr("id"));
            var marker = this.model.getMarker();
            this.map.setView(marker.getLatLng(), 16);
            marker.addTo(this.map)
                .bindPopup(this.model.get("name"))
                .openPopup();
            return this;
        }

    });

    ns.SearchMapView = Backbone.View.extend({

        initialize: function () {
            _.bindAll(this, "selectionChanged");
            this.collection.on("reset", this.considerMapMove, this);
        },

        render: function (bbox) {
            this.createMap(bbox);
            return this;
        },

        createMap: function (bbox) {
            this.map = createMapWithStandardLayer(this.$el.attr("id"), bbox);
            this.map.addLayer(this.collection.getLayerGroup());
            this.map.on("moveend", this.selectionChanged);
        },

        selectionChanged: function () {
            if (this.hasMoved) {
                this.hasMoved = false;
                return;
            }
            this.trigger("moveend");
        },

        getBounds: function () {
            return this.map.getBounds().toBBoxString();
        },

        zoomToBounds: function (bounds) {
            if (bounds) {
                this.map.fitBounds(bounds);
                this.hasMoved = true;
            }
        },

        considerMapMove: function () {
            var collectionBounds = this.collection.getBounds();
            var outsideBounds = !this.map.getBounds().contains(
                collectionBounds
            );

            if (outsideBounds) {
                this.map.fitBounds(collectionBounds);
            }
        }
    });

}(Flod));
