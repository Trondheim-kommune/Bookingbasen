var Flod = window.Flod || {};

(function (ns, undefined) {
    'use strict';

    ns.FacilityImage = Backbone.Model.extend({
        urlRoot: '/api/facilities/v1/images/',
        getImageUrl: function (width, height) {
            if (width && height) {
                return this.get('url') +
                    "?width=" + width + "&height=" + height;
            }

            return this.get('url');
        },
        parse: function (response) {
            // flask-restful sets the status property if the request fails
            if (typeof response.status !== 'undefined') {
                this.error(response['__error__']);
                return null;
            } else {
                this.success();
                return response;
            }
        }
    });

    ns.FacilityImages = Backbone.Collection.extend({
        model: ns.FacilityImage
    });

    ns.FacilityImagesFormView = Backbone.View.extend({
        events: {
            'submit form': 'save'
        },
        initialize: function () {
            _.bindAll(this, 'save', 'imageSaved', 'error', 'success');

            this.editable = true;
            if (this.options) {
                if (!_.isNull(this.options.editable) && !_.isUndefined(this.options.editable)) {
                    this.editable = this.options.editable;
                }
            }

            this.model.on('change', this.render, this);
        },
        setEditable : function(editable) {
            this.$("button").prop('disabled', !editable);
            this.$("input").prop('disabled', !editable);
        },

        error: function (errors) {
            _.each(errors || {}, function (message, field) {
                var el = '#' + field + '-group';
                this.$(el).addClass('error');
                this.$(el + ' .help-inline').text(message);
            }, this);
        },
        success: function () {
            _.each(['title', 'image'], function (field) {
                var el = '#' + field + '-group';
                this.$(el).removeClass('error');
                this.$(el + ' .help-inline').text('');
            }, this);
        },
        imageSaved: function (image) {
            // Since this request runs within an iframe it will always
            // trigger success regardless of actual status code. The actual
            // status code is checked in FacilityImage.parse
            if (!image.isNew()) {
                this.model.get('images').add(image);
            }
        },
        imageNotSaved: function (image, response) {
            // 413 responses are returned by Flask directly as text/html, so
            // they won't get passed to ns.FacilityDocument.parse
            if (response.responseText.match(/^413 Request Entity Too Large/)
                    !== null) {
                image.error({'image': 'Maks filstørrelse er 20 MB'});
            }
        },
        render: function () {
            this.$el.html(_.template($(this.options.template).html(), {
                facility: this.model
            }));
            return this;
        },
        save: function (event) {
            if (typeof event !== 'undefined') {
                event.preventDefault();
            }
            var data = this.$('form').serializeArray(),
                image = new ns.FacilityImage();
            image.error = this.error;
            image.success = this.success;
            image.save(null, {
                data: data,
                iframe: true,
                files: this.$('form :file'),
                processData: false,
                success: this.imageSaved,
                error: this.imageNotSaved
            });
        }
    });

    ns.FacilityImageView = Backbone.View.extend({
        events: {
            'click input.destroy': 'destroy'
        },
        initialize: function () {
            _.bindAll(this, 'destroy');
            this.editable = this.options.editable;
        },
        render: function () {
            this.$el.html(_.template($(this.options.template).html(), {
                image: this.model
            }));
            return this;
        },
        destroy: function () {
            this.model.destroy();
            this.remove();
        }
    });

    ns.FacilityImagesView = Backbone.View.extend({
        initialize: function () {
            this.editable = true;
            if (this.options) {
                if (!_.isNull(this.options.editable) && !_.isUndefined(this.options.editable)) {
                    this.editable = this.options.editable;
                }
            }

            this.collection.on('add', this.render, this);
        },
        renderImage: function (model) {
            return new ns.FacilityImageView({
                editable: this.editable,
                model: model,
                template: '#facility-image-template'
            }).render().$el;
        },
        renderImageRow: function (models) {

            var row = $('<div class="row-fluid"><ul class="thumbnails"></ul></div>');
            return row.find(".thumbnails").append(
                _.map(models, this.renderImage, this)
            );
        },
        render: function () {
            var html = _.chain(this.collection.models)
                .groupBy(function (o, i) {
                    return Math.floor(i / 4);
                })
                .toArray()
                .map(this.renderImageRow, this)
                .value();
            this.$el.html(html);
            return this;
        }
    });

}(Flod));
