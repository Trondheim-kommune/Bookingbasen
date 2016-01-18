(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('TimeSlotTest', {

        "should parse start_time": function () {
            var time = "2013-09-04T17:00:00";
            var ts = new Flod.TimeSlot({"start_time": time});
            assert.equals(ts.get("start_time").format("YYYY-MM-DDTHH:mm:ss"), time);
        },

        "should parse end_time": function () {
            var time = "2013-09-04T18:03:00";
            var ts = new Flod.TimeSlot({"end_time": time});
            assert.equals(ts.get("end_time").format("YYYY-MM-DDTHH:mm:ss"), time);
        },

        "should return displayName": function () {
            var data = {"person": new Backbone.Model({"uri": "/persons/1", "name": "Navn Navnesen"})};
            var ts = new Flod.TimeSlot(data);
            assert.equals(ts.getDisplayName(), data.person.get("name"));
        },

        "should return person as displayName if organisation is null": function () {
            var data = {"organisation": {"uri": null}, "person": new Backbone.Model({"uri": "/persons/1", "name": "Navn Navnesen"})};
            var ts = new Flod.TimeSlot(data);
            assert.equals(ts.getDisplayName(), data.person.get("name"));
        },

        "should return person as displayName if organisation is null and person is a POJO": function () {
            var data = {"organisation": {"uri": null}, "person": {"uri": "/persons/1", "name": "Navn Navnesen"}};
            var ts = new Flod.TimeSlot(data);
            assert.equals(ts.getDisplayName(), data.person.name);
        },

        "should return  org name as displayName if set": function () {
            var data = {
                "person": new Backbone.Model({"uri": "/persons/1", "name": "Navn Navnesen"}),
                "organisation": {"uri": "/oranisations/1", "name": "Org 1"}
            };
            var ts = new Flod.TimeSlot(data);
            assert.equals(ts.getDisplayName(), data.organisation.name);
        },

        "should return blank displayName when no org or person": function () {
            var ts = new Flod.TimeSlot();
            assert.equals(ts.getDisplayName(), "");

            var ts2 = new Flod.TimeSlot({"organisation": {"uri": null}, "person": new Backbone.Model({"uri": null})});
            assert.equals(ts2.getDisplayName(), "");
        },

        "should return unknown when status not set": function () {
            var ts = new Flod.TimeSlot();
            assert.equals(ts.getStatus(), "unknown");
        },

        "should return the set status lowecased": function () {
            var ts = new Flod.TimeSlot({"status": "Granted"});
            assert.equals(ts.getStatus(), "granted");
        },

        "toJSON should return proper data": function () {
            var data = {
                "start_time": "2013-09-04T17:00:00",
                "end_time": "2013-09-04T17:30:00",
                "label": "",
                "person": new Backbone.Model({"uri": "/persons/1", "name": "Navn Navnesen"}),
                "organisation": {"uri": "/oranisations/1", "name": "Org 1"},
                "resource": {"uri": "/resources/1"},
                "status": "Denied"
            };
            var ts = new Flod.TimeSlot(data);
            assert.equals(_.omit(ts.toJSON(), "person"), _.omit(data, "person"));
            assert.equals(ts.toJSON().person.uri, data.person.get("uri"));
        },

        "toJSON should return proper data when person is a POJO": function () {
            var data = {
                "start_time": "2013-09-04T17:00:00",
                "end_time": "2013-09-04T17:30:00",
                "person": {"uri": "/persons/1", "name": "Navn Navnesen"},
                "organisation": {"uri": "/oranisations/1", "name": "Org 1"},
                "resource": {"uri": "/resources/1"},
                "status": "Denied"
            };
            var ts = new Flod.TimeSlot(data);
            assert.equals(ts.toJSON().person.uri, data.person.uri);
        },

        "should be able to change date": function () {
            var data = {
                "start_time": "2013-09-04T17:00:00",
                "end_time": "2013-09-04T17:30:00"
            };
            var ts = new Flod.TimeSlot(data);
            ts.changeDate(moment("2013-09-10"));
            assert.equals(ts.get("start_time").format("YYYY-MM-DDTHH:mm:ss"), "2013-09-10T17:00:00");
            assert.equals(ts.get("end_time").format("YYYY-MM-DDTHH:mm:ss"), "2013-09-10T17:30:00");
        },

        "should handle time only": function () {
            var data = {
                "start_time": "17:00:00",
                "end_time": "17:30:00"
            };
            var ts = new Flod.TimeSlot(data);

            var today = moment().format("YYYY-MM-DD");

            assert.equals(ts.get("start_time").format("YYYY-MM-DDTHH:mm:ss"), today + "T17:00:00");
            assert.equals(ts.get("end_time").format("YYYY-MM-DDTHH:mm:ss"), today + "T17:30:00");
        },

        "should be able to get slot duration": function () {
            var data = {
                "start_time": "2013-09-04T17:00:00",
                "end_time": "2013-09-04T18:30:00"
            };
            var ts = new Flod.TimeSlot(data);

            assert.equals(ts.getDuration(), 90);
        },

        "should be able to get slot duration when only time": function () {
            var data = {
                "start_time": "17:00:00",
                "end_time": "18:30:00"
            };
            var ts = new Flod.TimeSlot(data);

            assert.equals(ts.getDuration(), 90);
        },

        "should be able to set custom display_name": function () {
            var ts = new Flod.TimeSlot({"display_name": "TEST"});
            assert.equals(ts.getDisplayName(), "TEST");
        }
    });


    buster.testCase('TimeSlotCollisionTest', {

        setUp: function () {
            this.timeSlot = new Flod.TimeSlot({
                    "start_time": "2013-09-04T15:30:00",
                    "end_time": "2013-09-04T17:30:00"
            });

            this.nocollision = new Flod.TimeSlot({
                "start_time": "2013-09-04T11:00:00",
                "end_time": "2013-09-04T12:00:00"
            });

            this.same = new Flod.TimeSlot({
                "start_time": "2013-09-04T15:30:00",
                "end_time": "2013-09-04T17:30:00"
            });

            this.rightAfter = new Flod.TimeSlot({
                "start_time": "2013-09-04T17:30:00",
                "end_time": "2013-09-04T19:30:00"
            });

            this.rightBefore = new Flod.TimeSlot({
                "start_time": "2013-09-04T14:30:00",
                "end_time": "2013-09-04T15:30:00"
            });
            this.overlaps = new Flod.TimeSlot({
                "start_time": "2013-09-04T14:30:00",
                "end_time": "2013-09-04T16:30:00"
            });
            this.covers = new Flod.TimeSlot({
                "start_time": "2013-09-04T14:30:00",
                "end_time": "2013-09-04T19:30:00"
            });
            this.covered = new Flod.TimeSlot({
                "start_time": "2013-09-04T16:00:00",
                "end_time": "2013-09-04T17:00:00"
            });
            this.anotherDay = new Flod.TimeSlot({
                "start_time": "2013-09-05T14:30:00",
                "end_time": "2013-09-05T16:30:00"
            });
        },

        "does not report totally different": function () {
            refute(this.timeSlot.collidesWith(this.nocollision));
        },


        "does not report collision with itself": function () {
            refute(this.timeSlot.collidesWith(this.timeSlot));
        },

        "does not report adjacent after": function () {
            refute(this.timeSlot.collidesWith(this.rightAfter));
        },

        "does not report adjacent before": function () {
            refute(this.timeSlot.collidesWith(this.rightBefore));
        },

        "does not report another day": function () {
            refute(this.timeSlot.collidesWith(this.anotherDay));
        },

        "detects overlap collision": function () {
            assert(this.timeSlot.collidesWith(this.overlaps));
        },

        "reports covers collision": function () {
            assert(this.timeSlot.collidesWith(this.covers));
        },

        "reports covered collision": function () {
            assert(this.timeSlot.collidesWith(this.covered));
        },

        "reports same collision": function () {
            assert(this.timeSlot.collidesWith(this.same));
        }

    });
}(Flod));