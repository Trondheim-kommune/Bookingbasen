var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var MainImageView = Backbone.View.extend({

        template: $("#image_template").html(),

        render: function () {
            this.$el.html(_.template(this.template, this.model.toJSON()));
            return this;
        }
    });

    var ThumbnailView = Backbone.View.extend({

        tagName: "li",

        className: "span3",

        template: $("#thumbnail_template").html(),

        events: {
            "click": "showImage"
        },

        initialize: function () {
            _.bindAll(this, "showImage");
        },

        render: function () {
            this.$el.html(_.template(this.template, this.model.toJSON()));
            return this;
        },

        showImage: function () {
            this.model.trigger("show", this.model);
        }
    });

    var ThumbnailsView = Backbone.View.extend({

        template: $("#thumbnails_template").html(),

        offset: 0,

        numElements: 3,

        events: {
            "click .icon-chevron-left": "scrollLeft",
            "click .icon-chevron-right": "scrollRight"
        },

        initialize: function () {
            _.bindAll(this, "scrollLeft", "scrollRight");
        },

        render: function () {
            if (this.collection.length > 0) {
                this.$el.html(_.template(this.template));
                var thumbs = _.map(this.collection.slice(this.offset, this.offset + this.numElements), function (image) {
                    return new ThumbnailView({"model": image}).render().$el;
                });

                this.$(".arrow:first").after(thumbs);
            }
            return this;
        },

        scrollLeft: function () {
            if (this.offset > 0) {
                this.offset -= 1;
                this.render();
            }
        },

        scrollRight: function () {
            if ((this.offset + this.numElements) < this.collection.length) {
                this.offset += 1;
                this.render();
            }
        }
    });

    var ImageViewer = ns.ImageViewer = Backbone.View.extend({

        template: $("#image_viewer_template").html(),

        initialize: function () {
            this.mainView = new MainImageView();
            this.thumbnailsView = new ThumbnailsView();
            this.collection.on("show", this.selectImage, this);
        },

        render: function () {
            this.$el.html(_.template(this.template));
            this.mainView.setElement(this.$(".main-image"));
            this.thumbnailsView.setElement(this.$(".thumbs"));
            this.selectImage(this.collection.at(0));
            return this;
        },

        selectImage: function (image) {
            this.mainView.model = image;
            image.set({"main": true});
            this.mainView.render();

            this.thumbnailsView.collection = new Backbone.Collection(
                this.collection.filter(function (img) {
                    return (img.id !== image.id);
                })
            );
            this.thumbnailsView.render();
        }
    });
}(Flod));