(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('WeeklyBlockedTimeTest', {
        "should be defined": function () {
            assert(ns.WeeklyBlockedTime);
        },

        "should have start_date and week_day": function () {
            var startDate = "2013-10-13";
            var weekDay = 2;
            var response = {
                "id": 1,
                "resource": {
                    "id": 1,
                    "uri": "/uri/1"
                },
                "start_date": startDate,
                "start_time": "10:00:00",
                "end_date": "2014-10-13",
                "end_time": "12:00:00",
                "week_day": weekDay
            };

            Backbone.$ = {
                "ajax": this.stub().yieldsTo("success", response)
            };

            var blocked = new ns.WeeklyBlockedTime({id: "1"});
            blocked.fetch();

            assert.calledOnce(Backbone.$.ajax);
            assert.equals(blocked.get("id"), 1);
            assert.equals(blocked.get("start_date"), startDate);
            assert.equals(blocked.get("week_day"), weekDay);
        },
        "should not be allowed to set a start date after end date": function () {
            var startDate = "2013-11-14";
            var endDate = "2013-11-12";
            var startTime = "10:00:00";
            var endTime = "12:00:00";

            var blocked = new ns.WeeklyBlockedTime({
                start_date: startDate,
                end_date: endDate,
                start_time: startTime,
                end_time: endTime
            });

            Backbone.$ = {
                "ajax": this.stub().yieldsTo("success", {'id': 123})
            };

            blocked.save();
            assert.equals(blocked.validationError.length, 1);

        },
        "should not be allowed to set a start time after end time on same date": function () {
            var startDate = "2013-11-12";
            var endDate = "2013-11-12";
            var startTime = "10:00:00";
            var endTime = "08:00:00";

            var blocked = new ns.WeeklyBlockedTime({
                start_date: startDate,
                end_date: endDate,
                start_time: startTime,
                end_time: endTime
            });

            Backbone.$ = {
                "ajax": this.stub().yieldsTo("success", {'id': 123})
            };

            blocked.save();
            assert.equals(blocked.validationError.length, 1);

        }
    });

    buster.testCase('WeeklyBlockedTimeCollectionTest', {
        "should be defined": function () {
            assert(ns.WeeklyBlockedTimeCollection);
        },

        "should fetch from correct location for a given resource": function () {
            var response = [];
            Backbone.$ = {
                "ajax": this.stub().yieldsTo("success", response)
            };
            var resource_uri = "/resource/1";
            var collection = new ns.WeeklyBlockedTimeCollection([], {resource_uri: resource_uri});
            collection.fetch();

            assert.calledOnce(Backbone.$.ajax);
            var expectedUrl = "/api/booking/v1/weeklyblockedtimes/?resource_uri=" + resource_uri;
            assert.calledWith(Backbone.$.ajax, sinon.match({url: expectedUrl}));
            assert.equals(collection.length, 0);
        }
    });

    buster.testCase('BlockedTimeIntervalTest', {
        "should be defined": function () {
            assert(ns.BlockedTimeInterval);
        },

        "should have start_time and end_time": function () {
            var startTime = "2013-10-13T10:00";
            var endTime = "2013-10-13T12:00";
            var response = {
                "id": 1,
                "resource": {
                    "id": 1,
                    "uri": "/uri/1"
                },
                "start_time": startTime,
                "end_time": endTime
            };

            Backbone.$ = {
                "ajax": this.stub().yieldsTo("success", response)
            };

            var blocked = new ns.BlockedTimeInterval({id: "1"});
            blocked.fetch();

            assert.calledOnce(Backbone.$.ajax);
            assert.equals(blocked.get("id"), 1);
            assert.equals(blocked.get("start_time"), startTime);
            assert.equals(blocked.get("end_time"), endTime);
        },

        "should convert the datetimes to dates and times in splitDatetimes method": function () {
            var startTime = "2013-11-14T10:00";
            var endTime = "2013-11-16T12:00";
            var id = 3;

            var blocked = new ns.BlockedTimeInterval({
                id: id,
                start_time: startTime,
                end_time: endTime
            });

            var display = blocked.splitDatetimes();
            assert.equals(display["start_date"], "14.11.2013");
            assert.equals(display["end_date"], "16.11.2013");
            assert.equals(display["start_time"], "10:00");
            assert.equals(display["end_time"], "12:00");
        },

        "should not be allowed to set a start date after end date": function () {
            var startTime = "2013-11-14T10:00";
            var endTime = "2013-11-12T12:00";
            var id = 3;

            var blocked = new ns.BlockedTimeInterval({
                id: id,
                start_time: startTime,
                end_time: endTime
            });

            Backbone.$ = {
                "ajax": this.stub().yieldsTo("success", {'id': 123})
            };
            blocked.save();

            assert.equals(blocked.validationError.length, 1);
        }

    });

}(Flod));
