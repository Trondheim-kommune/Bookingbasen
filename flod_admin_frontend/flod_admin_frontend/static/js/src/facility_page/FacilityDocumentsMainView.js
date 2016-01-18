var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.FacilityDocumentsMainView = Backbone.View.extend({

        initialize: function () {
            this.form = new Flod.FacilityDocumentsFormView({
                editable: this.options.editable,
                model: this.model,
                el: this.$('#facility-documents-form'),
                template: '#facility-documents-form-template'
            });

            this.list = new Flod.FacilityDocumentsView({
                editable: this.options.editable,
                collection: this.model.get('documents'),
                el: this.$('#facility-documents'),
                template: '#facility-documents-template'
            });
        },

        render: function () {
            this.form.render();
            this.list.render();
        }
    });

}(Flod));