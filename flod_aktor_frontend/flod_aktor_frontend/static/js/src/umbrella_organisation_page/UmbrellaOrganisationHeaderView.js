var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    ns.UmbrellaOrganisationHeaderView = Backbone.View.extend({

        initialize: function () {
            _.bindAll(this, 'render');

            if (this.model.isNew()) {
                this.model.once("sync", this.render, this);
            } else {
                this.render();
            }

            this.model.on('sync', this.updateHeader, this);
        },

        updateHeader: function () {
            this.$('h1').text(this.model.get('name'));
        },

        render: function () {

            // NOTE: {id:"home",title:"Informasjon"} is not here, as the view is not rendered here, but just updated!
            var tabs = [
                {id: "member_organisations", title: "Medlemsorganisasjoner"},
                {id: "responsible_persons", title: "Ansvarlige personer"}];

            if (this.model.isNew()) {
                _.each(tabs, function (tab) {
                    this.$("#" + tab.id + "Tab").addClass("disabled");
                    this.$("#" + tab.id + "Tab > a").prop("href", "javascript: void(0)");
                }, this);
            } else {
                _.each(tabs, function (tab) {
                    this.$("#" + tab.id + "Tab").removeClass("disabled");
                    this.$("#" + tab.id + "Tab > a").prop("href", "#" + tab.id);
                }, this);
            }
            this.updateHeader();
            return this;
        }
    });
}(Flod));
