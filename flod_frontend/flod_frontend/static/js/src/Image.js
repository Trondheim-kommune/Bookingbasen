var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";
    ns.Image = Backbone.Model.extend({

        getImageUrl: function (width, height) {
            if (width && height) {
                return this.get('url') +
                    "?width=" + width + "&height=" + height;
            }

            return this.get('url');
        },

        toJSON: function () {
            var data = _.clone(this.attributes);
            data.thumbnail = this.getImageUrl(70, 50);
            data.fullsize = this.getImageUrl(360, 270);
            return data;
        }
    });

    ns.Images = Backbone.Collection.extend({
        model: ns.Image
    });
}(Flod));
