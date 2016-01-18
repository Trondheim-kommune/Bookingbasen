var Flod = this.Flod || {};
(function (ns) {
    'use strict';

    var CalendarView = Backbone.View.extend({

        initialize: function () {

            var data = {
                "resource": this.model,
                "date": moment().format("YYYY-MM-DD"),
                "colorizeApplicants": true
            };
            this.calendarView = new ns.SingleCalendar({
                "data": data
            });
            this.calendarView.on("resetRows", this.resetRows, this);
            this.calendarView.on("slotsAdded", this.slotsAdded, this);
            this.calendarView.weeksChooser.on('changeWeek', this.slotsAdded,
                                              this);
        },

        slotsAdded: function () {
            var slots = this.calendarView.calendar.getSlots();
            this.trigger('slotsAdded', slots);
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

        render: function () {
            var cal = this.calendarView.render();
            cal.$el.addClass("calendar_wrapper");
            cal.$el.append($("#calendar_legend_template").html());
            this.$el.html(cal.$el);

            return this;
        }
    });

    var LegendView = Backbone.View.extend({

        tagName: "table",

        className: "table table-bordered legend",

        render: function () {
            var template = "<tr>" +
                "<td class='other' style='background-color: <%= color %>; width: 25px'></td>" +
                "<td><%= name %></td>" +
                    "</tr>";

            var rows = this.collection.map(function (legend) {
                return $(_.template(template, legend));
            });
            this.$el.empty();
            this.$el.append(rows);
            return this;
        }

    });

    ns.FacilityCalendarView = Backbone.View.extend({

        isRendered: false,

        updateEmailView: function (slots) {
            var emails = _.chain(slots)
                    .map(function (slot) {
                        return slot.get('applicant_email');
                    })
                    .compact()
                    .uniq()
                    .value();
            this.emailView.emails = emails;
        },

        updateLegendView: function (slots) {
            var legends = _.chain(slots)
                    .map(function (slot) {
                        var name = slot.get("applicant_name") ||
                                slot.get("display_name");
                        return {
                            "name": name,
                            "color": slot.get("color")
                        };
                    })
                    .uniq(false, function (legend) {
                        return legend.name;
                    })
                    .reject(function (legend) {
                        return legend.name === null;
                    })
                    .value();
            this.legendView.collection = legends;
            this.legendView.render();
        },

        render: function () {
            if (!this.isRendered) {
                this.isRendered = true;
                this.calendarView = new CalendarView({
                    "model": this.model,
                    "el": this.$el.find("#calendar_wrapper")
                });
                this.emailView = new ns.OrganisationEmailView({
                    "emails": []
                });

                this.legendView = new LegendView({
                    "collection": [],
                    "el": this.$el.find("#calendar_legend")
                });
                this.calendarView.on('slotsAdded', this.updateEmailView, this);
                this.calendarView.on('slotsAdded', this.updateLegendView, this);

                this.calendarView.render();
                this.legendView.render();
                this.emailView.render();
            }
            return this;
        }
    });

}(Flod));
