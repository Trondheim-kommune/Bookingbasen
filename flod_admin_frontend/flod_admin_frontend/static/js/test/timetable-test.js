(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('TimetableTest', {

        setUp: function () {

            this.applications = [
                {
                    "status": "Pending",
                    "resource": {"uri": "/facilities/1", "name": "Name", "id": 1},
                    "text": "ewqwq",
                    "requested_repeating_slots": [
                        {"resource": {"id": 1, "uri": "/facilities/1"},
                            "end_date": "2013-10-24",
                            "start_time": "10:00:00",
                            "week_day": 3,
                            "end_time": "19:30:00",
                            "start_date": "2013-09-24"
                        }
                    ],
                    "person": {"name": "Test Testesen1", "uri": "/persons/1"},
                    "organisation": {"num_members": 42, "uri": "/organisations/2", "name": "Test organisasjon 2"},
                    "id": 2,
                    "application_time": "2013-09-24T23:58:23.306991"
                },
                {
                    "status": "Pending",
                    "resource": {"uri": "/facilities/1", "name": "Name", "id": 1},
                    "text": "ewqwq",
                    "requested_repeating_slots": [
                        {"resource": {"id": 1, "uri": "/facilities/1"},
                            "end_date": "2013-10-24",
                            "start_time": "13:00:00",
                            "week_day": 1,
                            "end_time": "20:30:00",
                            "start_date": "2013-09-24"
                        }
                    ],
                    "person": {"name": "Test Testesen1", "uri": "/persons/1"},
                    "organisation": {"num_members": 42, "uri": "/organisations/1", "name": "Test organisasjon 1"},
                    "id": 3,
                    "application_time": "2013-10-24T23:58:23.306991"
                }
            ];

        },

        "//Should PUT applications back as repeating_slots with status Tentative": function () {

            Backbone.$ = {
                "ajax": this.stub().yieldsToAsync("success", [])
            };
            var applications = new Flod.Applications([this.applications[0]]);
            applications.save();
            assert.calledOnce(Backbone.$.ajax);
            var data = JSON.parse(Backbone.$.ajax.args[0][0].data);
            assert.equals(data.status, "Pending");
            assert.equals(data.repeating_slots.length, 1);
            assert.equals(data.repeating_slots[0].status, "Tentative");
        },

        "//should call callback after all applications PUTed": function () {

            var response = function (request){
                console.log("..");
                request.respond();
            };
            var server = sinon.fakeServer.create();
            server.respondWith(response);
            server.autoRespond = true;
            var spy = this.spy();

            var applications = new Flod.Applications(this.applications);
            console.log(applications.length);
            applications.save(spy);
            //assert.calledTwice(server);
            assert.calledOnce(spy);
            //assert(spy.calledAfter(server));
            server.restore();
        }
    });
    
}(Flod));