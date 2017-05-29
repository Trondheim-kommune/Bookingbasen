(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('StrotimeBookingViewTest', {

        setUp: function () {

            this.facility_types = [
                {"id": 1, "name": "Auditorium"},
                {"id": 2, "name": "Bibliotek"},
                {"id": 3, "name": "Dansesal"},
                {"id": 4, "name": "Gymsal"}
            ];

            this.facilities = [
                {"uri": "/facilities/1", "name": "test 1", "facility_type": {"id": 1, "name": "Auditorium"}, "id": 1},
                {"uri": "/facilities/2", "name": "test 2", "facility_type": {"id": 2, "name": "Bibliotek"}, "id": 2},
                {"uri": "/facilities/3", "name": "test 3", "facility_type": {"id": 2, "name": "Bibliotek"}, "id": 3}
            ];

            $("body").append('<script type="text/template" id="strotime_type_selector_template"><form></form></script>');
        },

        "Booking view should render dropdown with available facility types": function () {
            var el = $("<div></div>");
            var bookingView = new ns.StrotimeBookingView({
                "el": el,
                "facility_types": this.facility_types
            }).render();
            assert(el.find("select").length);
            assert.equals(el.find("select").children().length, 5);

            assert.equals($(el.find("select").children()[0]).html(), "Auditorium");
            assert.equals($(el.find("select").children()[1]).html(), "Bibliotek");
            assert.equals($(el.find("select").children()[2]).html(), "Dansesal");
            assert.equals($(el.find("select").children()[3]).html(), "Gymsal");
            assert.equals($(el.find("select").children()[4]).html(), "---");
            assert.equals($(el.find("select").children()[4]).attr("selected"), "selected");

        },

        "should re-render calendar on select": function () {

            var responses = [
                [{"unit_name": "Berg skole", "webpage": null, "accessibility": {"wheelchair_wc": "True", "available_by_wheelchair": "True", "elevator": "True"}, "images": [], "unit_phone_number": "72540370", "id": 61, "documents": [], "capacity": 266, "district": {"id": 3, "name": "Trondheim \u00d8st"}, "floor": "0", "facility_type": {"id": 7, "name": "Gymsal/treningsrom"}, "unit_type": {"id": 2, "name": "Skole"}, "equipment": {"sound_equipment": "True"}, "amenities": {"shower": "True", "wardrobe": "True"}, "short_description": "", "conditions": null, "unit_number": "021010", "description": "", "suitability": {"sport": "True"}, "address": "Bergsbakken 17", "is_deleted": false, "room": "3", "unit_email_address": "berg-skole.postmottak@trondheim.kommune.no", "name": "Berg skole gymsal", "short_code": null, "area": 0, "uri": "/facilities/61", "department_name": "", "unit_leader_name": "Cato H\u00f8ve", "position": {"lat": 63.41969681336524, "lon": 10.415798343124044}, "contact_person": {"phone_number": "41655672", "name": "Eirik Hansen"}, "is_published": true}],
                [],
                [],
                []
            ];

            var ajaxSpy = this.stub(Backbone.$, "ajax");
            ajaxSpy.onCall(0).yieldsTo("success", responses[0]);
            ajaxSpy.onCall(1).yieldsTo("success", responses[1]);
            ajaxSpy.onCall(2).yieldsTo("success", responses[2]);
            ajaxSpy.onCall(3).yieldsTo("success", responses[3]);

            var el = $("<div></div>");

            var bookingView = new ns.StrotimeBookingView({
                "el": el,
                "facility_types": this.facility_types,
                "facilities": this.facilities
            }).render();
            var spy = this.spy(bookingView.calendar, "setResources");
            $(el.find("select").children()[0]).trigger("select");
            assert.called(spy);
            assert.equals(spy.args[0][0].length, 1);

            assert.equals(ajaxSpy.callCount, 3);
        },

        "change day should re-render calendar": function () {
            // Using the stub as a spy since we do NOT want to call the backend with ajax
            // We dont need data from backend, therefore an empty array suffices as return value for all
            var ajaxSpy = this.stub(Backbone.$, "ajax").yieldsTo("success", []);

            var el = $("<div></div>");

            var bookingView = new ns.StrotimeBookingView({
                "el": el,
                "facility_types": this.facility_types,
                "facilities": this.facilities,
                "startDate": moment("2015-04-20")
            }).render();

            var calendar = bookingView.calendar;
            calendar.setResources(new Backbone.Collection(this.facilities[0])); // 3 calls
            assert.equals(ajaxSpy.callCount, 2);

            var sunday = $($(bookingView.calendar.weekView.$("tbody").children()[0]).children()[7]);
            sunday.trigger("click"); // 3 calls
            assert.equals(ajaxSpy.callCount, 4);

            var next = $($(bookingView.calendar.weekView.$(".flod-btn #right")));
            next.trigger("click"); // 3 calls
            assert.equals(ajaxSpy.callCount, 6);

            var friday = $($(bookingView.calendar.weekView.$("tbody").children()[0]).children()[6]);
            friday.trigger("click"); // 3 calls
            assert.equals(ajaxSpy.callCount, 8);

            var fridayAgain = $($(bookingView.calendar.weekView.$("tbody").children()[0]).children()[6]);
            assert(fridayAgain.hasClass("selected")); // 0 calls
            assert.equals(ajaxSpy.callCount, 8);

            var weekview = bookingView.calendar.weekView;
            weekview.trigger("changeDay",moment("2015-04-30")); // 3 calls
            assert.equals(ajaxSpy.callCount, 10);

            assert.equals($($(bookingView.calendar.$("thead").children()[0]).children()[0]).html(), "Torsdag");
            assert.equals($($(bookingView.calendar.$("thead").children()[1]).children()[0]).html(), "30.4");
        }
    });

    buster.testCase('StrotimeCalendarViewTest', {

        setUp: function () {
            this.facilities = [
                {"uri": "/facilities/1", "name": "test 1", "facility_type": {"id": 1, "name": "Auditorium"}, "id": 1},
                {"uri": "/facilities/2", "name": "test 2", "facility_type": {"id": 2, "name": "Bibliotek"}, "id": 2}
            ];
        },

        "calendar should fetch slots for right resources on setResources": function () {

            this.stub(Backbone.$, "ajax").yieldsTo(
                "success", [
                    {
                        "status": "Pending",
                        "resource": {"id": 2, "uri": "/facilities/2"},
                        "start_time": "2013-09-10T11:30:00",
                        "id": 18,
                        "organisation": {"uri": null},
                        "end_time": "2013-09-10T12:00:00",
                        "person": {"uri": "/persons/1"}
                    }
                ]
            );

            var test = {"reset": function (data) {}};

            var calendar = new Flod.StrotimeCalendar();
            var spy = this.spy(calendar.calendar.model, "reset");
            calendar.render(); // 0 calls
            calendar.setResources(new Backbone.Collection(this.facilities[0]));
            assert.calledTwice(Backbone.$.ajax); // 3 calls

            assert.equals(Backbone.$.ajax.args[0][0].url, "/api/booking/v1/slots/?resource_uri=%2Ffacilities%2F1&slot_duration=30&day=" + moment().add("days",3).format("YYYY-MM-DD") + "&status=Granted");
            assert.equals(Backbone.$.ajax.args[1][0].url, "/api/booking/v1/resources/facilities/1/blockedtimes/?date=" + moment().add("days",3).format("YYYY-MM-DD"));

            assert.calledOnce(spy);
            assert.equals(calendar.resources.at(0).get("slots").length, 1);

            var data = spy.args[0][0];
            assert.equals(data[0].displayName, "test 1");
        }

    });

}(Flod));