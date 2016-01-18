var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var isoDateFormat = "YYYY-MM-DD";
    var displayDateFormat = "DD.MM.YYYY";

    var convertDateFormat = function (value) {
        return moment(value, displayDateFormat).format(isoDateFormat);
    };

    var convertTimeFormat = function(value) {
        try {
            return moment(value, "H:mm").format("HH:mm");
        } catch (e) {
            return "";
        }
    };

    ns.BlockedTimeIntervalItemView = Backbone.View.extend({
        template: $("#blocked_time_interval_template").html(),
        tagName: "li",
        events: {
            "click #remove_button": "removeModel"
        },

        initialize : function () {
            this.editable = this.options.editable;
        },

        removeModel: function () {
            // Kill kill kill
            this.model.collection.remove(this.model);
            this.unbind();
            this.remove();
            this.model.destroy();
        },

        render: function () {
            var outputHtml = _.template(this.template, this.model.splitDatetimes());
            this.$el.html(outputHtml);
            return this;
        }
    });

    ns.BlockedTimeIntervalView = Backbone.View.extend({
        events: {
            "click #createNew": "createNew"
        },

        initialize: function () {
            _.bindAll(this, "add");

            if (this.options) {
                if (!_.isNull(this.options.editable) && !_.isUndefined(this.options.editable)) {
                    this.editable = this.options.editable;
                }
            }

            // bind this view to the add and remove events of the collection!
            this.collection.bind('add', this.add);

            // Provide usable default values for blocked time
            this.$("#start_time").val("8:00");
            this.$("#end_time").val("16:00");

            var today = moment();
            this.$("#start_date").val(today.format(displayDateFormat));
            this.$("#end_date").val(moment().add("weeks", 1).format(displayDateFormat));

            this.formValidation = new ns.FormValidationMixin({
                el: this.$("#blocked_time_interval_form_validation")
            });
        },

        createNew: function (event) {
            event.preventDefault();

            var startTime = convertTimeFormat(this.$("#start_time").val());
            var endTime = convertTimeFormat(this.$("#end_time").val());
            var startDate = convertDateFormat(this.$("#start_date").val());
            var endDate = convertDateFormat(this.$("#end_date").val());
            var note = this.$("#blocked_time_interval_note").val();

            // This will break (silently) if eiter startTime or startDate is an empty string

            var resource_uri = this.model.get('uri');
            var data = {
                "start_time": startDate + "T" + startTime,
                "end_time": endDate + "T" + endTime,
                "note": note,
                "resource_uri": resource_uri
            };

            var self = this;
            var model = new ns.BlockedTimeInterval(data);
            this.formValidation.setModel(model);
            model.save({}, {
                success: function () {
                    var data = {
                        title: "Suksess!",
                        text: "Blokkeringsperiode ble lagret.",
                        type: ns.Message.MessageType.SUCCESS
                    };
                    var messageModel = new ns.Message(data);
                    self.formValidation.showFormAlert(messageModel);
                    self.collection.add(model);
                },
                error : function (model, xhr, options) {
                    var error = JSON.parse(xhr.responseText);
                    var errorString = error["__error__"].join(", ");

                    var data = {
                        title: "Feil!",
                        text: error.message || errorString,
                        type: ns.Message.MessageType.ERROR
                    };
                    var messageModel = new ns.Message(data);
                    self.formValidation.showFormAlert(messageModel);
                }
            });
        },

        add: function (weeklyBlockedTime) {
            this.processItem(weeklyBlockedTime);
        },

        processItem: function (item) {
            var childItemView = new ns.BlockedTimeIntervalItemView({
                model: item,
                editable : this.editable
            });
            childItemView.render();
            this.$("#blocked_time_interval_list").append(childItemView.el);
        },

        render: function () {
            this.collection.each(this.processItem);
            return this;
        }
    });

}(Flod));
