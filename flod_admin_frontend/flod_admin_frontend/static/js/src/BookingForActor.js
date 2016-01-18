var Flod = window.Flod || {};

(function (ns, undefined) {
    "use strict";

    var Type = Backbone.Model.extend({
        defaults: {
            active: true,
            selected: false
        }
    });

    var Types = Backbone.Collection.extend({
        model: Type
    });

    var ToggleBtns = Backbone.View.extend({

        className: 'btn-group',

        events: {
            'click button': 'select'
        },

        btnTemplate: $('#toggle_btn_template').html(),

        render: function () {

            this.$el.html(this.collection.map(function (model) {
                return _.template(
                    this.btnTemplate,
                    model.toJSON()
                );
            }, this));

            return this;
        },

        select: function (e) {

            var element = $(e.currentTarget);
            if (!element.hasClass('c')) {
                var value = element.val();
                this.$('button.active').removeClass('active');
                element.addClass('active');
                this.trigger('changeType', value);
            }
        }
    });

    var ApplicationTypeSelect = Backbone.View.extend({

        className: 'span4',

        template: $('#booking_type_template').html(),

        initialize: function () {
            this.toggleBtns = new ToggleBtns({
                collection: new Types([
                    {text: "Engangslån", type: 'single', selected: true},
                    {text: "Fast lån", type: 'repeating'}
                ])
            });
            this.toggleBtns.on('changeType', this.changeType, this);
        },

        render: function () {
            this.$el.html(_.template(this.template));
            this.$('#booking-type').append(this.toggleBtns.render().$el);
            return this;
        },

        changeType: function (type) {
            this.trigger('changeType', type);
        }

    });

    var SingleBookingType = Backbone.View.extend({
        template: $('#single_booking_type_template').html(),
        events: {
            'click [type="checkbox"]': 'clicked'
        },
        render: function () {
            this.$el.html(_.template(this.template));
            return this;
        },
        clicked: function (event) {
            this.trigger('changeType', event.currentTarget.checked);
        },
        setBookingType: function (type) {
            if (type === 'repeating') {
                this.$el.hide();
            } else {
                this.render();
                this.$el.show();
            }
        }
    });


    var Facilities = Backbone.Collection.extend();

    var ResourceSelect = Backbone.View.extend({

        className: 'span4',

        template: $('#resource_select_template').html(),

        events: {
            'change select': 'change'
        },

        setType: function (type) {
            this.type = type;
            this.render();
        },

        render: function () {

            this.$el.html(_.template(this.template));
            var type = this.type;
            var elements = _.chain(this.collection.models)
                .filter(function (model) {
                    if (type === 'repeating') {
                        return model.get('repeating_booking_allowed');
                    } else if (type === 'single') {
                        return model.get('single_booking_allowed');
                    }
                })
                .map(function (model) {
                    return _.template(
                        '<option value="<%= id %>"><%= name %></option>',
                        model.toJSON()
                    );
                }).value();
            elements.unshift('<option>---</option>');
            this.$('select').html(elements);

            this.trigger('changeResource');

            return this;
        },

        change: function (e) {
            var resource = this.collection.get($(e.currentTarget).val());
            this.trigger('changeResource', resource);
        }

    });

    var Person = Backbone.Model.extend({
        getName: function () {
            return this.get('last_name') + ', ' + this.get('first_name');
        }
    });

    var Persons = Backbone.Collection.extend({
        model: Person
    });

    var Organisation = Backbone.Model.extend({
        getName: function () {
            return this.get('name');
        }
    });

    var Organisations = Backbone.Collection.extend({
        model: Organisation
    });

    var ActorChooser = Backbone.View.extend({

        template: $('#select_form_template').html(),

        event: 'changeActor',

        tagName: 'form',

        events: {
            'change select': 'change'
        },

        render: function () {
            this.$el.html(_.template(this.template, {label: this.label}));
            this.$('select').html('<option>--</option>');
            this.$('select').append(this.collection.map(function (model) {
                return _.template(
                    "<option value=<%=id %>><%= name %><% if (typeof national_identity_number !== 'undefined') { %> (<%= national_identity_number %>)<% } %></option>",
                    {id: model.id, name: model.getName(), national_identity_number: model.get('national_identity_number')}
                );
            }));
            this.trigger(this.event);
            return this;
        },

        change: function () {
            this.trigger(
                this.event,
                this.collection.get(this.$('select').val())
            );
        }

    });

    var PersonForActorChooser = ActorChooser.extend({
        event: 'changePersonForActor',
        label: 'Person'
    });

    var ActorSelect = Backbone.View.extend({

        className: 'span4',

        template: $('#actor_select_template').html(),

        initialize: function (options) {

            this.persons = options.persons;
            this.organisations = options.organisations;

            this.actorChooser = new ActorChooser({collection: this.persons});
            this.actorChooser.on('changeActor', this.changeActor, this);

            this.personForActorChooser = new PersonForActorChooser({
                collection: new Backbone.Collection()
            });

            this.personForActorChooser.on(
                'changePersonForActor',
                this.changePersonForActor,
                this
            );
            var types = [
                {text: "Enkeltperson", type: 'person', selected: true},
                {text: "Organisasjon", type: 'org'}
            ];

            this.toggleBtns = new ToggleBtns({
                collection: new Types(types)
            });
            this.type = 'person';
            this.toggleBtns.on('changeType', this.changeType, this);
        },

        render: function () {

            this.$el.html(_.template(this.template));
            this.$('.span8').append([
                this.toggleBtns.render().$el,
                '<hr>',
                this.actorChooser.render().$el
            ]);
            return this;
        },

        changeType: function (type) {
            this.type = type;
            if (type === 'person') {
                this.actorChooser.collection = this.persons;
                this.personForActorChooser.remove();
            } else {
                this.actorChooser.collection = this.organisations;
                this.$('.span8').append(
                    this.personForActorChooser.render().$el
                );
            }
            this.actorChooser.render();
        },

        setBookingType: function (type) {
            if (type === 'repeating') {
                this.changeType('org');
                this.$('button[value=person]')
                    .prop('disabled', true)
                    .removeClass('active');
                this.$('button[value=org]').addClass('active');
            } else {
                this.$('button[value=person]').prop('disabled', false);
            }
        },

        changeActor: function (actor) {

            if (!actor && this.personForActorChooser.collection.length) {
                this.personForActorChooser.collection.reset();
                this.personForActorChooser.render().delegateEvents();
            }

            if (actor instanceof Organisation) {
                this.personForActorChooser.collection = new Persons(
                    actor.get('persons')
                );
                this.personForActorChooser.render().delegateEvents();

                this.actor = actor;

            } else {
                this.trigger('changeActor', {person: actor});
            }
        },

        changePersonForActor: function (personForActor) {
            this.trigger('changeActor', {
                organisation: this.actor,
                person: personForActor
            });
        }
    });

    var TypeSelectRow = Backbone.View.extend({

        className: 'row-fluid',

        initialize: function (options) {
            this.typeSelect = new ApplicationTypeSelect();
            this.resourceSelect = new ResourceSelect({
                collection: options.facilities
            });
            this.resourceSelect.type = 'single';
            this.actorSelect = new ActorSelect({
                persons: options.persons,
                organisations: options.organisations
            });
            this.singleBookingType = new SingleBookingType();

            this.typeSelect.on('changeType', this.changeBookingType, this);
            this.resourceSelect.on('changeResource', this.changeResource, this);
            this.actorSelect.on('changeActor', this.changeActor, this);
            this.singleBookingType.on('changeType', this.changeSingleBookingType, this)
        },

        render: function () {
            this.$el.append([
                this.typeSelect.render().$el,
                this.resourceSelect.render().$el,
                this.actorSelect.render().$el
            ]);
            this.$el.find("#single-booking-application-type").append(this.singleBookingType.render().$el);
            return this;
        },

        changeBookingType: function (bookingType) {
            this.resourceSelect.setType(bookingType);
            this.actorSelect.setBookingType(bookingType);
            this.singleBookingType.setBookingType(bookingType);
            this.trigger('changeBookingType', bookingType);
        },

        changeResource: function (resource) {
            this.trigger('changeResource', resource);
        },

        changeActor: function (actor) {
            this.trigger('changeActor', actor);
        },

        changeSingleBookingType: function (isArrangement) {
            this.trigger('changeSingleBookingType', isArrangement);
        }

    });

    var CalendarView = Backbone.View.extend({
        tagName: "form",
        id: "booking_form",
        show: function (type, resource, actor, isArrangement) {
            if (this.calendar) {
                this.calendar.remove();
            }

            if (type === 'single') {
                this.calendar = new ns.SingleBookingView({
                    "date": moment(),
                    "resource": resource,
                    "showAsColors": isArrangement,
                    "facilitation_type_mappings": this.options.facilitation_type_mappings,
                    "facilitation_group_mappings": this.options.facilitation_group_mappings
                }).render();
            } else {
                this.calendar = new ns.RepeatingBookingView({
                    "resource": resource,
                    "facilitation_type_mappings": this.options.facilitation_type_mappings,
                    "facilitation_group_mappings": this.options.facilitation_group_mappings
                }).render();
            }

            this.calendar.extraData = {
                organisation: actor.organisation,
                person: actor.person,
                isArrangement: isArrangement
            };

            this.$el.append(this.calendar.$el);
        },

        hide: function () {
            if (this.calendar) {
                this.calendar.remove();
            }
        }

    });

    ns.BookingForActorView = Backbone.View.extend({

        initialize: function (options) {

            this.facilities = new Facilities(options.facilities);
            this.typeSelectRow = new TypeSelectRow({
                facilities: this.facilities,
                persons: new Persons(options.persons),
                organisations: new Organisations(options.organisations)
            });

            this.calendarView = new CalendarView({
                "facilitation_type_mappings": this.options.facilitation_type_mappings,
                "facilitation_group_mappings": this.options.facilitation_group_mappings
            });

            this.legendView = new ns.LegendView({
                "statuses": [
                    {"status": "collision", "text": "Konflikt"},
                    {"status": "rammetid", "text": "Rammetid fordelt til særidrettskretser"},
                    {"status": "reserved", "text": "Enheten har blokkert tid"},
                    {"status": "granted", "text": "Godkjent søknad"}
                ]
            });

            this.bookingType = 'single';
            this.isArrangement = false;
            this.typeSelectRow.on('changeBookingType', this.typeBookingChanged, this);
            this.typeSelectRow.on('changeResource', this.resourceChanged, this);
            this.typeSelectRow.on('changeActor', this.actorChanged, this);
            this.typeSelectRow.on('changeSingleBookingType', this.singleBookingTypeChanged, this)
        },

        render: function () {
            this.$el.html(this.typeSelectRow.render().$el);
            this.$el.append(this.calendarView.render().$el);
            $(".legend").html(this.legendView.render().$el);
            this.calendarView.hide();
            return this;
        },

        typeBookingChanged: function (bookingType) {
            this.bookingType = bookingType;
            this.showCalendar();
        },

        resourceChanged: function (resource) {
            this.resource = resource;
            this.showCalendar();
        },

        actorChanged: function (actor) {
            this.actor = actor;
            this.showCalendar();
        },

        singleBookingTypeChanged: function (isArrangement) {
            this.isArrangement = isArrangement;
            this.showCalendar();
        },

        showCalendar: function () {

            if (this.bookingType && this.resource && this.actor.person) {
                this.calendarView.show(
                    this.bookingType,
                    this.resource,
                    this.actor,
                    this.isArrangement
                );
            } else {
                this.calendarView.hide();
            }
        }

    });

}(Flod));
