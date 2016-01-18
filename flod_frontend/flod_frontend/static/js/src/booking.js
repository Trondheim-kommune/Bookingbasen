var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    //fix trouble with datepicker closing the whole modal
    $.fn.datepicker.Constructor.prototype.hide = function () {
        this.picker.hide();
    };

    var BookingFormFieldsetView = Backbone.View.extend({

        tagName: "fieldset",

        render: function () {
            this.$el.html(_.template(this.template, this.options.data));
            return this;
        }
    });

    var TextBoxView = BookingFormFieldsetView.extend({
        template: $("#booking_textbox_template").html(),

        getData: function () {
            var data = {};
            data[this.options.data.id] = this.$("textarea").val();
            return data;
        }
    });

    var FacilitationView = BookingFormFieldsetView.extend({
        template: $("#booking_facilitation_template").html(),

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

        getData: function () {
            var data = $('#booking_form').serializeObject();
            _.each(this.options.data.facilitation_group_mappings, function (type_val, type_key, obj) {
                data[type_key] = this.extractDict(type_key + '_', data);
            }, this);
            return data;
        }
    });

    function extendData(data, other) {

        var now = new ns.TimeSlot(data);
        other.push(now);

        var start = _.min(other, function (slot) {
            var d = moment(now)
                .hours(slot.get('start_time').hours())
                .minutes(slot.get('start_time').minutes());
            return d.valueOf();
        }).get('start_time');

        var end = _.max(other, function (slot) {
            var d = moment(now)
                .hours(slot.get('end_time').hours())
                .minutes(slot.get('end_time').minutes());
            return d.valueOf();
        }).get('end_time');

        data.start_time.hours(start.hours()).minutes(start.minutes());
        data.end_time.hours(end.hours()).minutes(end.minutes());
        return data;
    }

    var BookingCalendarMixin = {
        emptySlotClick: function (data) {
            var row = data.row;

            data = _.extend(_.omit(data, "row"), {
                "person": window.loggedInUser,
                "organisation": this.organisation,
                "resource": this.resource
            });

            //check to see if this slot can be merged with other new ones
            var other = row.filter(function (slot) {
                return (slot.get('status') === 'Unknown') && ns.isNextTo(data, slot);
            });
            if (other.length) {
                data = extendData(data, other);
                _.each(other, function (slot) {
                    row.removeSlot(slot);
                });
            }

            var slot = new Flod.TimeSlot(data);
            row.addSlot(slot);
            this.trigger("slotAdded", slot);
        },

        getData: function () {
            var slots = _.filter(this.calendar.getSlots(), function (slot) {
                return (slot.getStatus() === "unknown");
            });
            return {"slots": slots};
        },

        changeDisplayName: function (organisation) {
            this.organisation = organisation;
            var name = window.loggedInUser.get("name");
            if (organisation) {
                name = organisation.name;
            }
            _.each(this.calendar.getSlots(), function (slot) {
                if (slot.getStatus() === "unknown") {
                    slot.set("display_name", name);
                }
            });
        },

        clearSlots: function () {
            var remove = this.getData().slots;
            _.each(remove, function (slot) {
                slot.collection.removeSlot(slot);
            });
        },

        addSlots: function (slots) {
            var added = _.map(slots, function (slot) {
                var row = this.calendar.row(slot.week_day - 1);
                if (row) {
                    return row.addSlot(slot);
                }
                return false;
            }, this);

            return (added.indexOf(true) !== -1);
        }
    };

    var UserInfoView = Backbone.View.extend({

        template: $("#booking_userinfo_template").html(),

        tagName: "fieldset",

        events: {
            "change #id_organisation": "changeOrg"
        },

        initialize: function () {
            _.bindAll(this, "changeOrg");
        },

        render: function () {
            this.$el.html(_.template(this.template, {
                "type": this.options.type,
                "name": this.model.get("name"),
                "id": this.model.get("id"),
                "organisations": this.options.organisations
            }));
            this.$el.append("<hr>");

            if (this.options.type === 'repeating') {
                this.changeOrg();
            }
            return this;
        },

        getData: function () {
            var organisation_uri = this.$("#id_organisation").val();

            var organisation = _.find(this.options.organisations, function (organisation) {
                return (organisation.uri === organisation_uri);
            });

            return {
                "organisation": organisation,
                "person": window.loggedInUser,
                "resource": this.model.get("name")
            };
        },

        changeOrg: function () {
            var val = this.$("#id_organisation").val();

            var organisation = _.find(this.options.organisations, function (org) {
                return (org.uri === val);
            });
            this.trigger("changeOrganisation", organisation);
        }
    });

    var BookingDataView = Backbone.View.extend({

        template: $("#booking_confirm_template").html(),

        render: function (type) {
            var data = this.model.getDisplayData();
            data.type = type;
            data.facilitation_type_mappings = this.options.facilitation_type_mappings;
            data.facilitation_group_mappings = this.options.facilitation_group_mappings;
            this.$el.html(_.template(this.template, data));
            return this;
        }
    });

    var DatesSelect = Backbone.View.extend({

        template: $("#dates_select_template").html(),

        className: "row-fluid",

        initialize: function () {
            _.bindAll(this, 'dateChanged');
        },

        render: function () {
            this.$el.html(_.template(this.template));

            this.$("#start_date_div").datepicker({
                "format": 'dd.mm.yyyy',
                "weekStart": 1,
                "autoclose": true
            })
                .on('changeDate', this.dateChanged)
                .datepicker('setDate', moment().toDate());

            this.$("#end_date_div").datepicker({
                "format": 'dd.mm.yyyy',
                "weekStart": 1,
                "autoclose": true
            })
                .on('changeDate', this.dateChanged)
                .datepicker('setDate', moment().add(1, "M").toDate());

            return this;
        },

        getDates: function () {
            return {
                "start_date": moment(this.$el.find("#start_date").val(), "DD.MM.YYYY"),
                "end_date": moment(this.$el.find("#end_date").val(), "DD.MM.YYYY")
            };
        },

        dateChanged: function () {
            this.trigger("dateChange", this.getDates());
        }
    });

    var BookingView = Backbone.View.extend({

        events: {
            "click .btn-primary": "confirmApplication",
            "click .delete": "delete"
        },

        initialize: function () {
            _.bindAll(this, "confirmApplication", "applicationSaved", "error");

            this.views = [];
            this.userinfoview = new UserInfoView({
                "type": this.type,
                "model": this.options.resource,
                "organisations": this.options.organisations
            });
        },

        render: function () {
            this.userinfoview.render();

            this.views.push(this.userinfoview);
            this.$el.append(this.userinfoview.$el);
            this.textBoxView = new TextBoxView({
                "data": {
                    "id": "text",
                    "header": "Søknadstekst",
                    "subheader": "Skriv en kort begrunnelse om hvorfor dere ønsker å låne dette lokalet og hva dere ønsker å bruke det til." + (this.type ==='repeating' ? "<br>(Du kan gjerne skrive inn to alternative lokaler)" : ""),
                    "number": 1
                }
            }).render();
            this.$el.append(this.textBoxView.$el);
            this.views.push(this.textBoxView);

            this.facilitationView = new FacilitationView({
                "data": {
                    "id": "facilitation",
                    "header": "Tilrettelegging",
                    "subheader": "Hak av de punktene som er aktuelle for dere. Ved bestilling av <strong>ressurser</strong> (vises kun for lokaler hvor dette kan bestilles) kan dere blir fakturert. Se mer informasjon på lokalets side, eller kontakt enheten som har lokalet. Det tas forbehold om at det som ønskes er tilgjengelig.",
                    "number": 2,
                    "facilitations": this.userinfoview.model.toJSON(),
                    "facilitation_type_mappings": this.options.facilitation_type_mappings,
                    "facilitation_group_mappings": this.options.facilitation_group_mappings
                }
            }).render();
            this.$el.append(this.facilitationView.$el);
            this.views.push(this.facilitationView);

            //we create this before the extra views because they may need to pass it info
            this.createCalendarView();
            this.calendarView.on('slotAdded', this.slotAdded, this);
            this.$el.append(this.createExtraViews());


            this.views.push(this.calendarView);

            this.userinfoview.on(
                "changeOrganisation",
                this.calendarView.changeDisplayName,
                this.calendarView
            );
            var s = "<p><strong>Velg tid</strong> Legg inn ønsket tidspunkt ved å trykke i kalenderen.";

            s = s + "</br><strong>Slett tid</strong> Hvis du vil fjerne valgt tid, kan du trykke på en eller flere tider og trykke på &quot;Slett tid&quot;."
            s = s + "<span class='pull-right'><button class='delete btn btn-danger' disabled>Slett tid</button></span>";

            s = s + "</p>";
            var t = this.$el.append(s);
            this.$el.append(this.calendarView.$el);
            this.$el.append($("#calendar_legend_template").html());

            this.$el.append(
                "<div class='fluid-row'>" +
                "<p class='pull-right'>" +
                "<button class='btn btn-primary' type='button' disabled>Send søknad</button>" +
                "</p>" +
                "</div>"
            );
            return this;
        },

        slotAdded: function () {
            this.$('.btn-primary').removeAttr("disabled");
        },

        slotsRemoved: function () {
            if (!this.calendarView.getData().slots || !this.calendarView.getData().slots.length) {
                this.$('.btn-primary').attr("disabled", "true");
            }
        },

        createCalendar: function () {
        },

        createExtraViews: function () {
            return [];
        },

        confirmApplication: function () {

            var data = _.reduce(this.views, function (data, view) {
                return _.extend(data, view.getData());
            }, {});

            this.application = new this.applicationType(data);

            this.application.set("resource", this.options.resource);
            this.modal = new Flod.Modal({
                "template_data": {
                    "title": "Bekreft søknad",
                    "btn_txt": "Send søknad",
                    "btn_cancel_txt": "Avbryt"
                }
            });

            this.modal.render();
            this.modal.$(".modal-body").html(new BookingDataView({
                    "model": this.application,
                    "facilitation_group_mappings": this.options.facilitation_group_mappings,
                    "facilitation_type_mappings": this.options.facilitation_type_mappings
                }
            ).render(this.type).$el);

            this.modal.on("submit", this.sendApplication, this);
            this.modal.show();
        },

        sendApplication: function () {
            this.modal.hide();
            this.modal = null;

            this.application.save({}, {"success": this.applicationSaved, "error": this.error});
        },

        undelegateEvents: function () {
            _.each(this.views, function (view) {
                view.undelegateEvents();
            });
            Backbone.View.prototype.undelegateEvents.apply(this, arguments);
        },

        applicationSaved: function (model, response, options) {

            _.each(this.calendarView.calendar.getSlots(), function (slot) {
                if (slot.getStatus() === "unknown") {
                    slot.collection.remove(slot);
                }
            });
            this.addSlots(response);

        },

        'delete': function (event) {
            event.preventDefault();
            if (this.selectedSlots.length) {
                _.each(this.selectedSlots, function (slot) {
                    slot.collection.removeSlot(slot);
                }, this);
            }
            this.toggleSlotSelect([]);
        },

        toggleSlotSelect: function (selectedSlots) {
            var canDelete = selectedSlots.length;
            if (canDelete) {
                this.$('.delete').prop('disabled', false);
            } else {
                this.$('.delete').prop('disabled', true);
            }
            this.selectedSlots = selectedSlots;
        },

        error: function (model, xhr, options) {
            var error = JSON.parse(xhr.responseText);
            var errorString = error["__error__"].join(", ");
            var notifier = new ns.Notifier().render(
                "En feil oppstod under booking:",
                error.message || errorString,
                "error"
            );
            this.$el.append(notifier.$el);
            notifier.el.scrollIntoView();
            $(".alert").removeClass("offset1");
        },

        updateSlot: function (slot_data) {
            slot_data.status = this.application.get("status");
            slot_data.editable = false;
            if (this.application.has("organisation")) {
                slot_data.display_name = _.find(this.options.organisations, function (organisation) {
                    return (organisation.uri === this.application.get("organisation").uri);
                }, this).name;

            } else {
                slot_data.display_name = window.loggedInUser.get("name");
            }
            return slot_data;
        }
    });

    var DateRangeSelectView = BookingFormFieldsetView.extend({

        template: $("#booking_date_range_template").html(),

        events: {
            'change #start_date': 'dateChanged'
        },

        initialize: function () {
            this.dateSelect = new DatesSelect();
            this.dateSelect.on('dateChange', _.bind(this.dateChanged, this));
        },

        render: function () {
            BookingFormFieldsetView.prototype.render.apply(this, arguments);
            this.$('.main').append(this.dateSelect.render().$el);
            return this;
        },

        getData: function () {
            return this.dateSelect.getDates();
        },

        dateChanged: function (dates) {
            this.trigger('dateChange', dates);
        }
    });

    var PreviousApplicationsView = BookingFormFieldsetView.extend({

        template: $("#prev_applications_template").html(),

        events: {
            "change #id_prev_application": "changeApplication"
        },

        initialize: function () {
            this.collection.on('reset', this.render, this);
            _.bindAll(this, 'changeApplication');
        },

        render: function () {
            this.options.data.applications = this.collection.map(function (application) {
                return {
                    id: application.get('id'),
                    text: "Søknad " + application.get('id'),
                    selected: (application.get('id') === this.selected)
                };
            }, this);

            BookingFormFieldsetView.prototype.render.apply(this, arguments);
            if (this.collection.length) {
                this.$el.show();
            } else {
                this.$el.hide();
            }

            if (this.selected) {
                var application = this.collection.get(this.selected);
                this.trigger("useApplication", application);
            }

            return this;
        },

        selectApplication: function (application_id) {
            this.selected = application_id;
        },

        changeApplication: function () {
            var val = this.$("#id_prev_application").val();
            var application = this.collection.get(val);
            this.trigger("useApplication", application);
        },

        getData: function () {
            return {};
        }
    });

    var PreviousApplicationsCollection = Backbone.Collection.extend({

        url: "/api/booking/v1/applications/",

        find: function (resource_uri, organisation_uri) {
            this.fetch({
                data: {
                    resource_uri: resource_uri,
                    organisation_uri: organisation_uri,
                    type: 'repeating',
                    status: 'Granted'
                },
                reset: true
            });
        }
    });

    var RepeatingBookingView = BookingView.extend({

        type: "repeating",

        applicationType: ns.RepeatingApplication,


        initialize: function () {
            BookingView.prototype.initialize.apply(this, arguments);
            this.userinfoview.on("changeOrganisation", this.getPrevApplications, this);
            this.previousApplicationsCollection = new PreviousApplicationsCollection();
        },

        createCalendarView: function () {
            var data = {
                "resource": this.options.resource
            };

            this.calendarView = new ns.RepeatingCalendar({
                "data": data
            });

            this.calendarView.on("emptySlotClick", this.emptySlotClick, this);
            this.calendarView.on("resetRows", this.resetRows, this);
            this.calendarView.on("otherFetched", this.checkClone, this);
            this.calendarView.on('toggleSlotSelect', this.toggleSlotSelect, this);
            this.calendarView.on('slotRemoved', this.slotsRemoved, this);
            this.calendarView.render();
        },

        createExtraViews: function () {
            var dateRangeSelectView = new DateRangeSelectView({
                "data": {
                    "id": "date_range",
                    "header": "Låneperiode",
                    "subheader": "Angi start- og sluttdato for låneperioden.",
                    "number": 3
                }
            }).render();
            this.calendarView.setDates(dateRangeSelectView.getData());
            dateRangeSelectView.on(
                'dateChange',
                this.calendarView.setDates,
                this.calendarView
            );
            this.views.push(dateRangeSelectView);

            var previousApplicationsView = new PreviousApplicationsView({
                collection: this.previousApplicationsCollection,
                "data": {
                    "id": "prev_applications",
                    "header": "Bruk tidligere søknad",
                    "subheader": "Velg en tidligere søknad som utgangspunkt for ny.",
                    "number": ''
                }
            }).render();

            if (this.options.clone_id) {
                previousApplicationsView.selectApplication(this.options.clone_id);
            }

            previousApplicationsView.on('useApplication', this.useApplication, this);

            this.views.push(previousApplicationsView);

            return [dateRangeSelectView.$el, previousApplicationsView.$el];
        },

        addSlots: function (response) {
            _.each(response.slots, function (slot) {
                slot = this.updateSlot(slot);
                this.calendarView.calendar.row(slot.week_day - 1).addSlot(slot);
            }, this);
        },

        getPrevApplications: function (organisation) {
            this.previousApplicationsCollection.find(
                this.options.resource.get("uri"),
                organisation.uri
            );
        },

        checkClone: function () {
            if (this.clone_from) {
                this.doUseApplication(this.clone_from);
            }
        },

        useApplication: function (application) {

            if (!this.calendarView.fetched) {
                this.clone_from = application;
                return;
            }
            this.doUseApplication(application);
        },

        doUseApplication: function (application) {
            this.calendarView.clearSlots();
            this.slotsRemoved();

            var text = '', facilitation = '';
            if (application) {
                text = application.get('text');
                facilitation = application.get('facilitation');
                var added = this.calendarView.addSlots(application.get('slots'));
                if (added) {
                    this.slotAdded();
                }
            }
            this.$('#id_text').val(text);
            this.$('#id_facilitation').val(facilitation);
        },

        applicationSaved: function (model, response, options) {
            BookingView.prototype.applicationSaved.apply(this, arguments);
            var notifier = new ns.Notifier().render(
                "Søknad mottatt",
                "Din søknad om lån av dette lokalet er mottatt. Søknaden blir behandlet av Utlånstjenesten. " +
                "Svar på søknaden blir sendt til e-postadressen som er registrert på aktøren som du har søkt på vegne av, " +
                "og til e-postadressen som er registrert på deg. Hvis du ikke mottar e-post fra oss kan du sjekke søppelpost-filteret i e-postprogrammet ditt.",
                "success"
            );
            this.$el.append(notifier.$el);
            notifier.el.scrollIntoView();
        }


    });
    _.extend(ns.RepeatingCalendar.prototype, BookingCalendarMixin);
    _.extend(ns.RepeatingCalendar.prototype, ns.SlotClickMixin);

    var SingleBookingView = BookingView.extend({

        type: "single",

        applicationType: ns.SingleApplication,

        createCalendarView: function () {
            var data = {
                "resource": this.options.resource,
                "date": moment(this.options.date)
            };

            this.calendarView = new ns.SingleCalendar({
                "data": data
            });

            this.calendarView.on("emptySlotClick", this.emptySlotClick, this);
            this.calendarView.on("resetRows", this.resetRows, this);
            this.calendarView.on('toggleSlotSelect', this.toggleSlotSelect, this);
            this.calendarView.on('slotRemoved', this.slotsRemoved, this);
            this.calendarView.render();
        },

        resetRows: function (days) {
            this.calendarView.calendar.reset(
                _.map(days, function (day) {
                    return {
                        "displayName": day.moment.format("dddd DD.MM"),
                        "date": day.moment
                    };
                })
            );
        },

        addSlots: function (response) {
            _.each(response.slots, function (slot) {
                slot = this.updateSlot(slot);

                var row = _.find(this.calendarView.calendar.get("rows"), function (row) {
                    return row.getDate().isSame(slot.start_time, "day");
                });
                row.addSlot(slot);
            }, this);
        },

        applicationSaved: function (model, response, options) {
            BookingView.prototype.applicationSaved.apply(this, arguments);
            var feedback_msg;
            if (!_.isNull(model.get('organisation'))) {
                feedback_msg = "Din søknad om lån av dette lokalet er mottatt. Søknaden blir behandlet av enheten som har ansvar for lokalet. " +
                    "Svar på søknaden blir sendt til e-postadressen som er registrert på aktøren som du har søkt på vegne av, " +
                    "og til e-postadressen som er registrert på deg. Hvis du ikke mottar e-post fra oss kan du sjekke søppelpost-filteret i e-postprogrammet ditt."
            } else {
                feedback_msg = "Din søknad om lån av dette lokalet er mottatt. Søknaden blir behandlet av enheten som har ansvar for lokalet. " +
                    "Svar på søknaden blir sendt til e-postadressen som er registrert på deg. Hvis du ikke mottar e-post fra oss " +
                    "kan du sjekke søppelpost-filteret i e-postprogrammet ditt."
            }

            var notifier = new ns.Notifier().render(
                "Søknad mottatt",
                feedback_msg,
                "success"
            );
            this.$el.append(notifier.$el);
            notifier.el.scrollIntoView();
        }
    });
    _.extend(ns.SingleCalendar.prototype, BookingCalendarMixin);
    _.extend(ns.SingleCalendar.prototype, ns.SlotClickMixin);

    var BookingTypeChooser = Backbone.View.extend({

        events: {
            "click #single": "selectSingle",
            "click #repeating": "selectRepeating"
        },

        initialize: function () {
            _.bindAll(this, "selectSingle", "selectRepeating");
            if (!this.model.get("repeating_booking_allowed") || !this.model.get("single_booking_allowed")) {
                this.$el.hide();
            }
        },

        selectSingle: function () {
            this.$("#repeating").parent().removeClass("active");
            this.$("#single").parent().addClass("active");
        },

        selectRepeating: function () {
            this.$("#repeating").parent().addClass("active");
            this.$("#single").parent().removeClass("active");
        }
    });

    ns.BookingRouter = Backbone.Router.extend({

        routes: {
            "": "index",
            "date/(:date)": "single",
            "clone/:clone_id": "index"
        },

        forms: {
            "single": {
                "header": "Søknad om engangslån",
                "view": SingleBookingView
            },
            "repeating": {
                "header": "Søknad om fast lån",
                "view": RepeatingBookingView
            }
        },

        initialize: function (data) {
            this.data = data;
            this.typeChooser = new BookingTypeChooser({
                "el": $("#booking_tabs"),
                "model": data.resource
            }).render();
            this.typeChooser.on("change", this.changeType, this);
        },

        index: function (clone_id) {
            if (!this.data.resource.get("repeating_booking_allowed")) {
                this.single();
                return;
            }
            this.type = "repeating";
            if (!clone_id) {
                this.navigate("", {"replace": true});
            }
            this.typeChooser.selectRepeating();
            this.render(clone_id);
        },

        single: function (date) {

            if (!date) {
                //if no date is given, start 21 days ahead in time as requested by customer
                date = moment().add('d', 21).format("YYYY-MM-DD");
                this.navigate("date/" + date, {"replace": true});
            }
            this.date = date;
            this.type = "single";
            this.typeChooser.selectSingle(true);
            this.render();
        },

        changeType: function (type) {
            this.type = type;
        },

        render: function (clone_id) {
            if (this.formView) {
                this.formView.undelegateEvents();
            }

            var form = this.forms[this.type];

            this.formView = new form.view(_.extend({
                "type": this.type,
                "date": this.date,
                "facilitation_type_mappings": this.data.facilitation_type_mappings,
                "facilitation_group_mappings": this.data.facilitation_group_mappings,
                "clone_id": parseInt(clone_id, 10)
            }, this.data)).render();
            $("#booking_form").html(this.formView.$el);
            $("#booking_header").html(form.header);
        }
    });

}(Flod));
