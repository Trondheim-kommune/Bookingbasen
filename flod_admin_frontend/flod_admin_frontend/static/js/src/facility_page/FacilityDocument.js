var Flod = window.Flod || {};

(function (ns, undefined) {
    'use strict';

    ns.FacilityDocument = Backbone.Model.extend({
        urlRoot: '/api/facilities/v1/documents/',
        getDocumentUrl: function () {
            return this.get('url');
        },
        parse: function (response) {
            if (typeof response.status !== 'undefined') {
                this.error(response['__error__']);
                return null;
            } else {
                this.success();
                return response;
            }
        }
    });

    ns.FacilityDocuments = Backbone.Collection.extend({
        model: ns.FacilityDocument
    });

    ns.FacilityDocumentsFormView = Backbone.View.extend({
        events: {
            'submit form': 'save'
        },
        initialize: function () {
            _.bindAll(this, 'save', 'documentSaved', 'error', 'success');

            this.editable = true;
            if (this.options) {
                if (!_.isNull(this.options.editable) && !_.isUndefined(this.options.editable)) {
                    this.editable = this.options.editable;
                }
            }

            this.model.on('change', this.render, this);
        },
        error: function (errors) {
            _.each(errors || {}, function (message, field) {
                var el = '#' + field + '-group';
                this.$(el).addClass('error');
                this.$(el + ' .help-inline').text(message);
            }, this);
        },
        success: function () {
            _.each(['title', 'document'], function (field) {
                var el = '#' + field + '-group';
                this.$(el).removeClass('error');
                this.$(el + ' .help-inline').text('');
            }, this);
        },
        documentSaved: function (doc) {
            // Request runs within iframe so any non-OK responses will be
            // caught in ns.FacilityDocument.parse
            if (!doc.isNew()) {
                this.model.get('documents').add(doc);
            }
        },
        documentNotSaved: function (doc, response) {
            // 413 responses are returned by Flask directly as text/html, so
            // they won't get passed to ns.FacilityDocument.parse
            if (response.responseText.match(/^413 Request Entity Too Large/)
                    !== null) {
                doc.error({'document': 'Maks filstørrelse er 20 MB'});
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
                doc = new ns.FacilityDocument();
            doc.error = this.error;
            doc.success = this.success;
            doc.save(null, {
                data: data,
                iframe: true,
                files: this.$('form :file'),
                processData: false,
                success: this.documentSaved,
                error: this.documentNotSaved
            });
        }
    });

    ns.FacilityDocumentView = Backbone.View.extend({
        events: {
            'click input.destroy': 'destroy'
        },
        initialize: function () {
            _.bindAll(this, 'destroy', 'remove');

            this.editable = this.options.editable;
        },

        render: function () {
            this.$el.html(_.template($(this.options.template).html(), {
                doc: this.model
            }));
            //this.setEditable(this.editable);
            return this;
        },
        destroy: function () {
            this.model.destroy({
                "success": this.remove,
                "error": function () {alert("oops!"); }
            });
        }
    });

    ns.FacilityDocumentsView = Backbone.View.extend({
        initialize: function () {
            if (this.options) {
                if (!_.isNull(this.options.editable) && !_.isUndefined(this.options.editable)) {
                    this.editable = this.options.editable;
                }
            }
            this.collection.on('add', this.render, this);
        },

        renderDocument: function (model) {
            var documentView = new ns.FacilityDocumentView({
                editable: this.editable,
                model: model,
                el: '<tr>',
                template: '#facility-document-template'
            });
            return documentView.render().$el;
        },
        render: function () {
            var documents = _.map(this.collection.models, this.renderDocument,
                                  this);
            this.$el.html(_.template($(this.options.template).html()));
            this.$el.find('tbody').append(documents);
            return this;
        }
    });

}(Flod));
