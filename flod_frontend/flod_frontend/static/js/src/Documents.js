var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var Document = Backbone.Model.extend({

        getUrl: function () {
            return this.get('url');
        },

        toJSON: function () {
            var data = _.clone(this.attributes);
            data.url = this.getUrl();
            return data;
        }
    });


    ns.Documents = Backbone.Collection.extend({
        model: Document
    });

    var DocumentView = Backbone.View.extend({

        template: $("#document_template").html(),

        className: "document",

        render: function () {
            this.$el.html(_.template(this.template, this.model.toJSON()));
            return this;
        }
    });

    ns.DocumentsView = Backbone.View.extend({

        className: "documents span12",

        render: function () {
            this.$el.append(this.collection.map(function (document) {
                return new DocumentView({"model": document}).render().$el;
            }));
            return this;
        }
    });

}(Flod));
