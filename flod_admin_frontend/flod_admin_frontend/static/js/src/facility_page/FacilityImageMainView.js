var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.FacilityImageMainView = Backbone.View.extend({

        initialize: function () {

            this.form = new Flod.FacilityImagesFormView({
                editable: this.options.editable,
                model: this.model,
                el: this.$('#facility-images-form'),
                template: '#facility-images-form-template'
            });

            this.list = new Flod.FacilityImagesView({
                editable: this.options.editable,
                collection: this.model.get('images'),
                el: this.$('#facility-images')
            });
        },

        render: function () {
            this.form.render();
            this.list.render();
        }
    });

}(Flod));


