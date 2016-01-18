var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    /**
     * A message object on the form  {title:"<title>",text:"<text>",type:"<type>"}; as input and shows message at top screen
     * @param title
     * @param text
     * @param type valid types: ["error","success"]
     */
    ns.Message = Backbone.Model.extend({

        defaults : {
            type : -1,
            title : '',
            message : ''
        },

        toString: function () {
            JSON.stringify(this.toJSON());
        }

    }, {
        MessageType :  {
            "DEFAULT": -1,
            "ERROR" : 0,
            "SUCCESS" : 1
        }
    });

    ns.MessageCollection = Backbone.Collection.extend({
        model: ns.Message
    });

    ns.MessageView = Backbone.View.extend({

	    tagName : "div",

	    className : "alert",

        id : "user_alert",

        events: {
            "click .close": "close"
        },

        template : $('#alert_template').html(),

        initialize: function () {

            var messageType = this.model.get('type');

            if (messageType === ns.Message.MessageType.ERROR) {
                this.$el.addClass('alert-danger');
            } else if (messageType === ns.Message.MessageType.SUCCESS) {
                this.$el.addClass('alert-success');
            } else {
                //fail
            }
        },

        render : function () {
            this.$el.html(_.template(this.template, this.model.attributes));
            return this;
        },

        close : function () {
            this.off();
            this.undelegateEvents();
            this.remove();
            this.model.destroy();
        }
    });

}(Flod));
