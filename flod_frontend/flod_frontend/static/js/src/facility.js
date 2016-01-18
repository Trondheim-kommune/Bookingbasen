var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var DetailsView = Backbone.View.extend({

        fixFacilityData: function (data) {
            var types = [
                "accessibility",
                "equipment",
                "amenities",
                "suitability",
                "facilitators"
            ];
            _.each(types, function (mapping_type) {
                data[mapping_type] = _.map(
                    data[mapping_type],
                    function (value, key) {
                        return this.options.type_mappings[mapping_type][key];
                    },
                    this
                );
            }, this);
            return data;
        },

        render: function () {
            var hasImages = (this.model.has("images") &&
            this.model.get("images").length);

            var data = this.fixFacilityData(this.model.toJSON());
            data["description"] = data["description"].replace(/\n/g, '<br/>');

            data.hasImages = hasImages;

            this.$el.html(_.template($("#details_template").html(), data));
            if (hasImages) {
                new Flod.ImageViewer({
                    "el": this.$("#images"),
                    "collection": new ns.Images(this.model.get("images"))
                }).render();
            }

            var hasDocuments = (this.model.has("documents") &&
            this.model.get("documents").length);

            if (hasDocuments) {
                this.$("#documents").append(
                    new ns.DocumentsView({
                        "collection": new ns.Documents(
                            this.model.get("documents")
                        )
                    }).render().$el
                );
            } else {
                this.$("#documents").hide();
            }

            return this;
        }
    });

    var CalendarView = Backbone.View.extend({

        initialize: function () {

            var data = {
                "resource": this.model,
                "date": moment().format("YYYY-MM-DD")
            };

            this.calendarView = new ns.SingleCalendar({
                "data": data
            });
            this.calendarView.on("resetRows", this.resetRows, this);
            this.calendarView.on("loadedSlots", this.renderLegend, this);
        },

        resetRows: function (days) {
            this.calendarView.calendar.reset(
                _.map(days, function (day) {
                    return {
                        "displayName": day.moment.format("dddd DD.MM"),
                        "date": day.moment
                    };
                })
            );
        },

        render: function () {

            var cal = this.calendarView.render();
            cal.$el.addClass("calendar_wrapper");
            this.$el.html(cal.$el);

            return this;
        },

        renderLegend: function () {
            this.$('.legend').remove();
            this.$el.append(
                _.template(
                    $("#calendar_legend_facility_template").html(),
                    {colors: this.calendarView.colorMap}
                )
            );
        }
    });

    var MapView = Backbone.View.extend({

        render: function () {
            var map = new Flod.SinglePointMapView({
                "model": this.model,
                "el": this.$("#map")
            }).render();
            return this;
        }
    });

    ns.FacilityView = Backbone.Router.extend({

        initialize: function (options) {
            this.options = options;

            if (!this.options.model.hasMarker()) {
                this.options.el.find("#map_tab").remove();
            }
        },

        routes: {
            "date:date": "details",
            "": "details",
            "calendar": "calendar",
            "map": "map"
        },

        details: function (date) {
            this.date = date;
            this.options.el.find("#details_tab").tab('show');
            new DetailsView({
                "model": this.options.model,
                "el": this.options.el.find(".tab-content"),
                "date": date,
                "type_mappings": this.options.type_mappings
            }).render();
        },

        calendar: function () {
            this.options.el.find("#calendar_tab").tab('show');
            new CalendarView({
                "model": this.options.model,
                "el": this.options.el.find(".tab-content")
            }).render();
        },

        map: function () {
            if (this.options.model.hasMarker()) {
                this.options.el.find("#map_tab").tab('show');
                var el = this.options.el.find(".tab-content");
                el.html(_.template($("#map_template").html()));
                new MapView({"model": this.options.model, el: el}).render();
            } else {
                this.details();
            }
        }
    });
}(Flod));
