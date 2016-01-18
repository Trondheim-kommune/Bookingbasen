var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.FacilityInternalNotesModel = Backbone.Model.extend({
        url: function () {
            var url = '/api/facilities/v1/facilities/' + this.get("facility").id + '/notes/';
            if (this.id) {
                url += this.id;
            }
            return url;
        }
    });

    ns.FacilityInternalNotesCollection = Backbone.Collection.extend({
        model: ns.FacilityInternalNotesModel,
        comparator: function (model) {
            // Sort notes by descending order.
            return -moment(model.get("create_time")).valueOf();
        }
    });

    ns.FacilityInternalNoteFormView = Backbone.View.extend({
        events: {
            'click #save-notat': 'save'
        },
        initialize: function () {
            _.bindAll(this, 'save', 'noteSaved');
        },
        noteSaved: function (note) {
            if (!note.isNew()) {
                // Clear text field.
                this.$el.find('#text').val("");
                this.options.FacilityInternalNotesCollection.add(note);
            }
        },
        save: function (event) {
            if (typeof event !== 'undefined') {
                event.preventDefault();
            }
            var note = new ns.FacilityInternalNotesModel({
                // The id of the current user that is logged in (hash string).
                auth_id: this.model.get("user").id,
                facility : {
                    id: this.model.get("id")
                },
                text: this.$el.find('#text').val(),
                // User is used for display only.
                user : {
                    id: this.model.get("user").id,
                    private_id: this.model.get("user").private_id
                }
            });
            note.save(null, {
                success: this.noteSaved
            });
        }
    });

    ns.FacilityInternalNoteView = Backbone.View.extend({
        events: {
            'click .destroy': 'destroy'
        },
        initialize: function () {
            _.bindAll(this, 'destroy', 'remove');
        },
        render: function () {
            this.$el.html(_.template($(this.options.template).html(), {
                note: this.model
            }));
            return this;
        },
        destroy: function () {
            this.model.destroy({
                "success": this.remove,
                "error": function () {
                    alert("Kunne ikke fjerne notatet!");
                }
            });
        }
    });

    ns.FacilityInternalNotesListView = Backbone.View.extend({
        initialize: function () {
            this.collection.on('add', this.add, this);
        },
        renderDocument: function (model) {
            var view = new ns.FacilityInternalNoteView({
                model: model,
                el: '<tr>',
                template: '#internal-notes-template'
            });
            return view.render().$el;
        },
        add: function (model) {
            this.render();
        },
        render: function () {
            var notes = _.map(this.collection.models, this.renderDocument, this);
            // Show list of notes inside tbody content.
            this.$el.find('tbody').html(notes);
            return this;
        }
    });

    ns.FacilityInternalNotesView = Backbone.View.extend({
        initialize: function () {
            // Create collection of internal notes
            var FacilityInternalNotesCollection =
                new ns.FacilityInternalNotesCollection(this.model.get("notes"));

            // Create new internal notes
            this.form = new ns.FacilityInternalNoteFormView({
                model: this.model,
                el: this.$('#notes-form'),
                editable: this.options.editable,
                FacilityInternalNotesCollection: FacilityInternalNotesCollection
            });

            // List all internal notes
            this.list = new ns.FacilityInternalNotesListView({
                editable: this.options.editable,
                collection: FacilityInternalNotesCollection,
                el: this.$('#notes-list')
            });
        },
        render: function () {
            this.form.render();
            this.list.render();
        }
    });

}(Flod));
