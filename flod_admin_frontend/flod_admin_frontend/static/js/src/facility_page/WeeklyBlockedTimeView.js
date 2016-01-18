var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var isoDateFormat = "YYYY-MM-DD";
    var displayDateFormat = "DD.MM.YYYY";

    var convertDateFormat = function (value) {
        return moment(value, displayDateFormat).format(isoDateFormat);
    };

    var convertTimeFormat = function (value) {
        try {
            return moment(value, "H:mm").format("HH:mm");
        } catch (e) {
            return "";
        }
    };

    var toInt = function (str) {
        return parseInt(str, 10);
    };

    ns.WeeklyBlockedTimeItemView = Backbone.View.extend({
        template: $("#weekly_blocked_time_template").html(),
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
            var outputHtml = _.template(this.template, this.model.toDisplay());
            this.$el.html(outputHtml);
            return this;
        }
    });

    ns.WeeklyBlockedTimeView = Backbone.View.extend({
        events: {
            "click #createNew": "createNew"
        },

        initialize: function () {
            _.bindAll(this, "add");

            // bind this view to the add and remove events of the collection!
            this.collection.bind('add', this.add);

            // Provide usable default values for blocked time
            this.$("#start_time").val("8:00");
            this.$("#end_time").val("16:00");

            var today = moment();
            this.$("#start_date").val(today.format(displayDateFormat));
            this.$("#end_date").val(moment().add("years", 1).format(displayDateFormat));

            this.formValidation = new ns.FormValidationMixin({
                "el": this.$("#weekly_blocked_time_form_validation")
            });
        },

        createNew: function (event) {
            event.preventDefault();

            var startTime = convertTimeFormat($("#start_time").val());
            var endTime = convertTimeFormat($("#end_time").val());
            var startDate = convertDateFormat($("#start_date").val());
            var endDate = convertDateFormat($("#end_date").val());
            var weekDay = toInt($("#week_day").val());
            var note = this.$("#blocked_note").val();
            var resource_uri = this.model.get('uri');
            var data = {
                "start_time": startTime,
                "end_time": endTime,
                "start_date": startDate,
                "end_date": endDate,
                "week_day": weekDay,
                "note": note,
                "resource_uri": resource_uri
            };

            var self = this;
            var model = new ns.WeeklyBlockedTime(data);
            this.formValidation.setModel(model);
            model.save({}, {
                success: function () {
                    var data = {
                        title: "Suksess!",
                        text: "Blokkeringsdag ble lagret.",
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
            var childItemView = new ns.WeeklyBlockedTimeItemView({
                model: item,
                editable : this.editable
            });
            childItemView.render();
            $("#weekly_list").append(childItemView.el);
        },

        render: function () {
            this.collection.each(this.processItem);
            return this;
        }
    });

    ns.WeeklyBlockedTimeEightToFourView = Backbone.View.extend({
        events: {
            "click #createNewEightToFour": "createNewEightToFour"
        },

        initialize: function () {
            this.start_time = "8:00";
            this.end_time = "16:00";

            var today = moment();
            this.$("#weekly_start_date").val(today.format(displayDateFormat));
            this.$("#weekly_end_date").val(moment().add("years", 1).format(displayDateFormat));

            this.formValidation = new ns.FormValidationMixin({
                "el": this.$("#weekly_blocked_time_eight_to_four_form_validation")
            });
        },

        createNewEightToFour: function (event) {
            event.preventDefault();

            var startTime = convertTimeFormat(this.start_time);
            var endTime = convertTimeFormat(this.end_time);
            var startDate = convertDateFormat($("#weekly_start_date").val());
            var endDate = convertDateFormat($("#weekly_end_date").val());
            var note = this.$("#weekly_blocked_note").val();
            var weekDay;
            var errors = [];
            var weekdays = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag"];

            for (weekDay = 1; weekDay <= 5; weekDay++) {
                var resource_uri = this.model.get('uri');
                var data = {
                    "start_time": startTime,
                    "end_time": endTime,
                    "start_date": startDate,
                    "end_date": endDate,
                    "week_day": weekDay,
                    "note": note,
                    "resource_uri": resource_uri
                };
                var self = this;
                var model = new ns.WeeklyBlockedTime(data);
                this.formValidation.setModel(model);
                var success = true;

                model.save({}, {
                    async: false,
                    success: function () {
                        self.collection.add(model);
                    },
                    error: function (model, xhr, options) {
                        success = false;
                        var error = JSON.parse(xhr.responseText);
                        var errorString = error["__error__"].join(", ");

                        errors.push(weekdays[weekDay-1] + ": " + (error.message || errorString));
                    }
                });
                if (success) {
                    var successData = {
                        title: "Suksess!",
                        text: "Blokkeringsdager ble lagret.",
                        type: ns.Message.MessageType.SUCCESS
                    };
                    var successMessageModel = new ns.Message(successData);
                    self.formValidation.showFormAlert(successMessageModel);
                } else {
                    var errorData = {
                        title: "Feil!",
                        text: errors.join(",<br/>"),
                        type: ns.Message.MessageType.ERROR
                    };
                    var errorMessageModel = new ns.Message(errorData);
                    self.formValidation.showFormAlert(errorMessageModel);
                }
            }
        }
    });

}(Flod));
