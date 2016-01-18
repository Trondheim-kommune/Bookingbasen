var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var SearchResults = Backbone.Collection.extend({

        baseUrl: "/api/facilities/v1/facilities",

        url: function () {
            var url = this.baseUrl;
            if (this.query) {
                url += "?name=" + encodeURIComponent(this.query);
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

    var ResultView = Backbone.View.extend({

        template: "<a tabindex='-1' href='/facilities/<%= id %>'><%=name %></a></li>",

        tagName: "li",

        render: function () {
            this.$el.html(_.template(this.template, this.model.toJSON()));
            return this;
        }
    });

    var ResultsView = Backbone.View.extend({

        initialize: function () {
            this.collection.on("reset", this.render, this);
        },

        render: function () {
            if (this.collection.length === 0) {
                this.$el.hide();
            } else {
                var elems = this.collection.map(function (result) {
                    return new ResultView({"model": result}).render().$el;
                });
                this.$el.html(elems);
                this.$el.show();
            }
        }
    });

    var QuickSearch = Backbone.View.extend({

        events: {
            "keyup .typeahead": "search"
        },

        initialize: function () {
            _.bindAll(this, "search");
            this.results = new SearchResults();
            this.resultsView = new ResultsView({"collection": this.results});
            this.results.on("reset", this.showResults, this);
        },

        render: function () {
            this.resultsView.setElement(this.$(".dropdown-menu"));
            return this;
        },

        search: function () {
            var val = $(".typeahead").val();
            if (val === "") {
                this.results.reset();
            } else {
                this.results.query = val;
                this.results.fetch({reset: true});
            }
        }
    });

    //fire it up
    new QuickSearch({"el": $("#quicksearch")}).render();

}(Flod));