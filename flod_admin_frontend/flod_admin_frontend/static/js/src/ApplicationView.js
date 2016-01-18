var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    //fix trouble with datepicker closing the whole modal
    $.fn.datepicker.Constructor.prototype.hide = function () {
        this.picker.hide();
    };

    var MessageView = Backbone.View.extend({

        template: $("#message_box_template").html(),

        render: function (text, email) {
            this.$el.html(_.template(
                this.template, {text: text, email: email}));

            return this;
        },

        getMessage: function () {
            return this.$("#message").val();
        },

        getInvoiceAmount: function () {
            return this.$("#invoice_amount").val();
        }
    });


    var FacilityChangeView = Backbone.View.extend({

        template: $("#facility_change_template").html(),

        initialize: function (options) {
            this.collection.on("reset", this.render, this);
        },

        render: function (facilities) {
            this.$el.html(_.template(this.template, {facilities: this.collection.toJSON()}));
            return this;
        },

        getSelectedFacility: function () {
            return this.collection.get(this.$("#selected_facility").val());
        }
    });

    var PeriodChangeView = Backbone.View.extend({
        template: $("#period_change_template").html(),

        initialize: function (options) {
            this.render(options.period);
        },

        render: function (period) {
            this.$el.html(_.template(this.template));

            this.$("#start_date_div").datepicker({
                "format": 'dd.mm.yyyy',
                "weekStart": 1,
                "autoclose": true
            })
                .datepicker('setDate', new Date(period.start_date));

            this.$("#end_date_div").datepicker({
                "format": 'dd.mm.yyyy',
                "weekStart": 1,
                "autoclose": true
            })
                .datepicker('setDate', new Date(period.end_date));
            return this;
        },

        getDates: function () {
            return {
                "start_date": moment(this.$el.find("#start_date").val(), "DD.MM.YYYY"),
                "end_date": moment(this.$el.find("#end_date").val(), "DD.MM.YYYY")
            };
        },

        showError: function (model) {
            var errorString = model["__error__"].join(", ");
            this.$("#validation").prepend(
                new ns.Notifier().render(
                    "En feil oppstod under booking:",
                    errorString,
                    "error"
                ).$el
            );
            $(".alert").removeClass("offset1");
        }
    });

    var ArrangementConflicts = Backbone.Collection.extend({
        model: ns.SimpleApplication,
        initialize: function (models, options) {
            options || (options = {});
            this.application_id = options.application_id;
        },
        url: function () {
            return "/api/booking/v1/arrangement_conflicts/" + this.application_id;
        }
    });

    var ArrangementNotification = Backbone.Model.extend({
        url: function () {
            return "/api/booking/v1/arrangement_notification/" + this.get("application_id");
        }
    });

    var ApplicationView = Backbone.View.extend({

        template: $("#application_template").html(),
        buttonsTemplate: $('#application_buttons_template').html(),

        events: {
            "click #approve": "approve",
            "click #deny": "deny",
            "click #save": "grant",
            "click #delete": "delete",
            "click #change_facility": "changeFacility",
            "click #change_period": "changePeriod",
            "click #show-send-email-affected-applications": "sendEmailAffectedApplications",
            "click #reprocess": "reprocess",
            "click #release_time": "release_time"
        },

        initialize: function () {
            _.bindAll(this, "error", "approve", "deny", "grant", "delete",
                "applicationApproved", "applicationGranted",
                "applicationDenied", "changeFacility", "changePeriod",
                "reprocess", "applicationReprocessed", "updateButtons",
                "affectedApplicationEmailSent",
                "affectedApplicationEmailError");
            this.createCalendarView();
            this.calendarView.on('toggleSlotSelect', this.toggleSlotSelect, this);

            document.title = this.model.get('requested_resource').name + " - Lånesøknad - Bookingbasen Admin";

            this.model.on("change:status", this.updateButtons, this);

            this.legendView = new ns.LegendView({
                "statuses": [
                    {"status": "pending", "text": "Avventer behandling"},
                    {"status": "processing", "text": "Behandles"},
                    {"status": "collision", "text": "Konflikt (klikk for å løse)"},
                    {"status": "rammetid", "text": "Rammetid"},
                    {"status": "reserved", "text": "Enheten har blokkert tid"},
                    {"status": "other", "text": "Annen søknad (klikk for å gå til)"},
                    {"status": "granted", "text": "Godkjent søknad"},
                    {"status": "denied", "text": "Avvist søknad"}
                ]
            });

            this.messageView = new MessageView();

            if (this.model.get("is_arrangement")) {
                this.applicationListView = new ns.ApplicationListView({
                    collection: this.options.arrangementConflicts
                });
            }
        },

        error: function (model, xhr, options) {
            var error = JSON.parse(xhr.responseText);
            var errorString = error["__error__"].join(", ");
            this.$(".calendar").after(
                new ns.Notifier().render(
                    "En feil oppstod:",
                    error.message || errorString,
                    "error",
                    10
                ).$el
            );
        },

        updateButtons: function () {
            var html = _.template(this.buttonsTemplate,
                this.model.toDetailDisplay());
            this.$("#buttons").html(html);
        },

        render: function () {
            var data = this.model.toDetailDisplay();
            data.facilitation_type_mappings = this.options.facilitation_type_mappings;
            data.facilitation_group_mappings = this.options.facilitation_group_mappings;
            this.$el.html(_.template(this.template, data));
            this.updateButtons();
            this.$(".calendar").append(this.calendarView.render().$el);
            this.$(".legend").append(this.legendView.render().$el);
            return this;
        },

        toggleSlotSelect: function (selectedSlots) {
            var canDelete = selectedSlots.length && (this.calendarView.getData().length > 1);
            if (canDelete) {
                this.$('#delete').prop('disabled', false);
            } else {
                this.$('#delete').prop('disabled', true);
            }
            this.selectedSlots = selectedSlots;
        },

        updateStatus: function (application, editable) {
            this.$("input").prop("disabled", !editable);
            this.$('#id_comment').prop("disabled", !editable);
            _.each(this.calendarView.getData(), function (slot) {
                slot.set("editable", !!editable);
                slot.set("status", application.get("status") + ' own-slot');
            });
        },

        extractDict: function (prefix, data) {
            var dict = {};
            _.each(data, function (value, key) {
                var sub = key.substring(0, prefix.length);
                if (sub === prefix) {
                    dict[key.slice(prefix.length)] = value;
                    delete data[key];
                }
            });
            return dict;
        },

        updateModel: function () {
            var data = this.$("form").serializeObject();

            // Extract the amenities (they share a prefix)
            this.model.set('amenities', this.extractDict("amenities_", data));
            this.model.set('accessibility', this.extractDict("accessibility_", data));
            this.model.set('equipment', this.extractDict("equipment_", data));
            this.model.set('suitability', this.extractDict("suitability_", data));
            this.model.set('facilitators', this.extractDict("facilitators_", data));
            this.model.set('comment', this.$("#id_comment").val());
        },

        approve: function () {
            this.updateModel();
            this.model.save(
                {
                    'slots': this.calendarView.getSlots(),
                    'status': 'Processing',
                    'include_emails': 'True'
                },
                {
                    'success': this.applicationApproved,
                    "error": this.error
                }
            );
        },

        applicationApproved: function (application) {
            this.updateStatus(application, true);
            this.$(".calendar").after(
                new ns.Notifier().render("Søknaden ble lagret", "", "success", 5).$el
            );
        },

        grant: function () {
            this.updateModel();
            this.modal = new Flod.Modal({
                "template_data": {
                    "title": "Godkjenn søknad",
                    "btn_txt": "Godkjenn",
                    "btn_cancel_txt": "Avbryt"
                }
            });

            this.modal.render();
            var email = this.model.get("emails")["granted_message"];
            this.modal.$(".modal-body").html(this.messageView.render(
                "Viktig informasjon til låntaker:", email).$el);

            this.modal.on("submit", _.bind(function () {
                var to_be_invoiced = this.modal.$("#id_to_be_invoiced").is(':checked');
                this.model.save(
                    {
                        'slots': this.calendarView.getSlots(),
                        'status': 'Granted',
                        'message': this.messageView.getMessage(),
                        'to_be_invoiced': to_be_invoiced
                        //'invoice_amount': this.messageView.getInvoiceAmount()
                    },
                    {
                        'success': this.applicationGranted,
                        "error": _.bind(function (model, xhr, options) {
                            this.model.set('status', this.model.previous("status"));

                            // Hide modal in order for user to see error message!
                            this.modal.hide();
                            this.modal = null;

                            this.error(model, xhr, options);
                        }, this)
                    }
                );
            }, this));
            this.modal.show();
        },

        applicationGranted: function (application) {
            this.updateStatus(application, false);
            this.$(".calendar").after(
                new ns.Notifier().render("Søknaden ble godkjent", "", "success", 5).$el
            );
            this.modal.hide();
            this.modal = null;
        },

        deny: function () {
            this.updateModel();
            this.modal = new Flod.Modal({
                "template_data": {
                    "title": "Avvis søknad",
                    "btn_txt": "Avvis",
                    "btn_cancel_txt": "Avbryt"
                }
            });

            this.modal.render();
            var email = this.model.get("emails")["denied_message"];
            this.modal.$(".modal-body").html(this.messageView.render(
                "Oppgi en begrunnelse for avslag:", email).$el);

            this.modal.on("submit", _.bind(function () {
                this.model.save(
                    {
                        'slots': this.calendarView.getSlots(),
                        'status': 'Denied',
                        'message': this.messageView.getMessage()
                    },
                    {
                        'success': this.applicationDenied,
                        "error": _.bind(function (model, xhr, options) {
                            this.model.set('status', this.model.previous("status"));

                            // Hide modal in order for user to see error message!
                            this.modal.hide();
                            this.modal = null;

                            this.error(model, xhr, options);
                        }, this)
                    }
                );
            }, this));
            this.modal.show();
        },

        reprocess: function () {
            this.modal = new Flod.Modal({
                "template_data": {
                    "title": "Behandle søknad på ny",
                    "btn_txt": "Behandle på ny",
                    "btn_cancel_txt": "Avbryt"
                }
            });
            this.modal.render();
            this.modal.$(".modal-body").html(
                "<p>Søknaden er allerede behandlet. " +
                "Ønsker du å behandle den på ny?</p>");

            this.modal.on("submit", _.bind(function () {
                this.model.save(
                    {
                        'status': 'Pending',
                        'slots': []
                    },
                    {
                        'success': this.applicationReprocessed,
                        'error': this.error
                    }
                );
            }, this));
            this.modal.show();
        },

        applicationReprocessed: function (application) {
            this.updateStatus(application, true);
            this.$(".calendar").after(
                new ns.Notifier().render(
                    "Søknaden behandles på ny", "", "success", 5).$el
            );
            this.modal.hide();
            this.modal = null;
        },

        applicationDenied: function (application) {
            this.updateStatus(application, false);
            this.$(".calendar").after(
                new ns.Notifier().render("Søknaden ble avvist", "", "success", 5).$el
            );
            this.modal.hide();
            this.modal = null;
        },

        changeFacility: function () {

            this.modal = new Flod.Modal({
                "template_data": {
                    "title": "Endre lokale",
                    "btn_txt": "Lagre",
                    "btn_cancel_txt": "Avbryt"
                }
            });

            var facilities = new ns.Facilities();
            var bookingType = this.model.get("type");
            facilities.url = "/facilities_by_booking_type/?type=" +
                bookingType;

            this.modal.render();
            var facilityChangeView =
                new FacilityChangeView({
                    collection: facilities,
                    el: this.modal.$(".modal-body")
                });

            this.modal.on("submit", _.bind(function () {
                var newFacility = facilityChangeView.getSelectedFacility();
                this.model.save(
                    {
                        'resource': {"uri": newFacility.get("uri")}
                    },
                    {
                        'success': this.informationChanged,
                        'error': this.error
                    }
                );
            }, this));

            facilities.fetch({reset: true});
            this.modal.show();
        },

        changePeriod: function () {
            this.modal = new Flod.Modal({
                "template_data": {
                    "title": "Endre periode",
                    "btn_txt": "Lagre",
                    "btn_cancel_txt": "Avbryt"
                }
            });

            this.modal.render();
            var periodChangeView = new PeriodChangeView({
                period: this.getChosenPeriod(),
                el: this.modal.$(".modal-body")
            });

            this.modal.on("submit", _.bind(function () {
                var newPeriod = periodChangeView.getDates();

                var newSlots = this.calendarView.getSlots().map(function (slot) {
                    return {
                        start_time: slot.start_time,
                        end_time: slot.end_time,
                        start_date: newPeriod.start_date.format("YYYY-MM-DDTHH"),
                        end_date: newPeriod.end_date.format("YYYY-MM-DDTHH"),
                        id: slot.id,
                        week_day: slot.week_day
                    };
                });

                var self = this;
                this.model.save(
                    {
                        'slots': newSlots
                    },
                    {
                        'success': this.informationChanged,
                        'error': function (model, xhr, options) {
                            var error = JSON.parse(xhr.responseText);
                            periodChangeView.showError(error);
                        }
                    }
                );
            }, this));

            this.modal.show();
        },

        getChosenPeriod: function () {
            if (this.model.slots.length > 0) {
                return {"start_date": this.model.slots[0].get("start_date"), "end_date": this.model.slots[0].get("end_date")}
            }
            else {
                return {"start_date": null, "end_date": null};
            }
        },

        informationChanged: function () {
            window.location.reload();
        },

        'delete': function () {
            //cannot delete unless there are at least two slots!
            if (this.calendarView.getSlots().length > 1) {
                if (this.selectedSlots.length) {
                    _.each(this.selectedSlots, function (slot) {
                        slot.collection.removeSlot(slot);
                        this.approve();
                    }, this);
                }
            }
        },

        affectedApplicationEmailSent: function () {
            this.$(".calendar").after(
                new ns.Notifier().render(
                    "Epost vil bli sendt til berørte søknader.",
                    "", "success", 5).$el
            );
            this.modal.hide();
            this.modal = null;
        },

        affectedApplicationEmailError: function () {
            this.$(".calendar").after(
                new ns.Notifier().render(
                    "En feil oppstod!", "Prøv igjen senere.",
                    "error", 5).$el
            );
            this.modal.hide();
            this.modal = null;
        },

        sendEmailAffectedApplications: function () {
            this.modal = new Flod.Modal({
                "template_data": {
                    "title": "Send epost til berørte søknader",
                    "btn_txt": "Ja",
                    "btn_cancel_txt": "Nei"
                },
                "template": $("#send-email-affected-applications-template")
            });
            this.modal.render();

            // List arrangements in modal
            if (this.model.get("is_arrangement")) {
                this.modal.$el.find(".arrangement_conflicts").append(
                    this.applicationListView.render().$el);
            }

            // Increase modal width
            this.modal.$el.css({
                "width": "auto",
                "height": "auto",
                "max-height": "100%",
                "margin-left": function () {
                    return -($(this).width() / 2);
                }
            });

            this.modal.on("submit", _.bind(function () {
                var application_id = this.model.get("id");
                var message = this.modal.$el.find("#message").val();
                var arrangementNotification = new ArrangementNotification({
                    application_id: application_id,
                    message: message
                });
                arrangementNotification.save({}, {
                    success: this.affectedApplicationEmailSent,
                    error: this.affectedApplicationEmailError
                }, this);
            }, this));
            this.modal.show();
        },
        release_time: function () {
            window.location.href = '/release_time/repeating_application/' + this.model.get('id');
        }
    });

    var SingleApplicationView = ApplicationView.extend({
        createCalendarView: function () {
            var data = {
                resource: new Backbone.Model(this.model.get('resource')),
                date: moment(this.model.get('slots')[0].start_time),
                facilitation_type_mappings: this.options.facilitation_type_mappings,
                facilitation_group_mappings: this.options.facilitation_group_mappings
            };

            this.calendarView = new ns.SingleCalendarView({
                data: data,
                model: this.model
            });
        }
    });

    var RepeatingApplicationView = ApplicationView.extend({
        createCalendarView: function () {
            var data = {
                resource: new Backbone.Model(this.model.get('resource')),
                facilitation_type_mappings: this.options.facilitation_type_mappings,
                facilitation_group_mappings: this.options.facilitation_group_mappings
            };

            this.calendarView = new ns.RepeatingCalendarView({
                "data": data,
                "model": this.model
            });
        }
    });

    var SingleApplication = ns.Application.extend({});

    var RepeatingApplication = ns.Application.extend({});

    ns.createApplicationView = function (application_data, arrangement_conflicts_data, facilitation_type_mappings, facilitation_group_mappings, element) {
        var model;
        if (application_data.type === 'single') {
            model = new SingleApplication(application_data);
            var arrangementConflicts = new ArrangementConflicts(arrangement_conflicts_data);
            return new SingleApplicationView({
                "model": model,
                "arrangementConflicts": arrangementConflicts,
                "facilitation_type_mappings": facilitation_type_mappings,
                "facilitation_group_mappings": facilitation_group_mappings,
                "el": element
            });
        }
        if (application_data.type === 'repeating') {
            model = new RepeatingApplication(application_data);
            return new RepeatingApplicationView({
                "model": model,
                "facilitation_type_mappings": facilitation_type_mappings,
                "facilitation_group_mappings": facilitation_group_mappings,
                "el": element
            });
        }
        throw new Error("Application must have a type!");
    };


}(Flod));
