var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.OrganisationInternalNotesModel = Backbone.Model.extend({
        url: function () {
            var url = '/api/organisations/v1/organisations/' + this.get("organisation_id") + '/notes/';
            if (this.id) {
                url += this.id;
            }
            return url;
        }
    });

	ns.OrganisationInternalNotesCollection = Backbone.Collection.extend({
		model: ns.OrganisationInternalNotesModel,
        comparator: function (model) {
            // Sort notes by descending order.
            return -moment(model.get("create_time")).valueOf();
        }
    });

    ns.OrganisationInternalNoteFormView = Backbone.View.extend({
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
                this.options.organisationInternalNotesCollection.add(note);
            }
        },
        save: function (event) {
            if (typeof event !== 'undefined') {
                event.preventDefault();
            }

            var note = new ns.OrganisationInternalNotesModel({
                // The id of the current user that is logged in (hash string). 
                organisation_id: this.model.get("id"),
                text: this.$el.find('#text').val(),
                // The list of notes uses the user properties to display content.
                user : {
                    id: window.loggedInUser.get('id'),
                    private_id: window.loggedInUser.get('private_id')
                }
            });
            //note.error = this.error;
            //note.success = this.success;
            note.save(null, {
                success: this.noteSaved
            });
        }
    });

    ns.OrganisationInternalNoteView = Backbone.View.extend({
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

    ns.OrganisationInternalNotesListView = Backbone.View.extend({
        initialize: function () {
            this.collection.on('add', this.add, this);
        },
        renderDocument: function (model) {
            var view = new ns.OrganisationInternalNoteView({
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

    ns.OrganisationInternalNotesView = Backbone.View.extend({
        initialize: function () {
            // Create collection of internal notes
            //var organisationInternalNotesCollection = new ns.OrganisationInternalNotesCollection(this.model.get("notes"));

            // Create new internal notes
            this.form = new ns.OrganisationInternalNoteFormView({
                model: this.model,
                el: this.$('#notes-form'),
                organisationInternalNotesCollection: this.collection
            });

            // List all internal notes
            this.list = new ns.OrganisationInternalNotesListView({
                collection: this.collection,
                el: this.$('#notes-list')
            });
        },
        render: function () {
            this.form.render();
            this.list.render();
        }
    });

}(Flod));