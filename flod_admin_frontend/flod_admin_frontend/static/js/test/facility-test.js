(function (ns) {
    "use strict";
    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;
    buster.testCase('FacilityTest', {
        "should be defined": function () {
            assert(ns.Facility);
        },

        "should have name and description": function () {
            var name = "Strindheim samfunnshus";
            var shortDescription = "Fantastic samfunnshus!";
            var response = {

                "id": 1,
                "short_description": shortDescription,
                "capacity": 10,
                "name": name,
                "webpage": "http://www.example.org",
                "images": [
                    {"filename": "f1", "id": 1, "title": "image title1"},
                    {"filename": "f2", "id": 2, "title": "image title2"}
                ],
                "position": {
                    "lat": 63.402,
                    "lon": 10.44
                },
                "contact_person": {
                    "phone_number": "12345678",
                    "name": "Navn Navnesen",
                    "email": "mail@mail.no"
                },
                "facility_type": {"id": 1, "name": "Auditorium"},
                "description": "desc"
            };

            Backbone.$ = {
                "ajax": this.stub().yieldsTo("success", response)
            };

            var fac = new ns.Facility({id: "1"});
            fac.fetch();

            assert.calledOnce(Backbone.$.ajax);
            assert.equals(fac.get("name"), name);
            assert.equals(fac.get("short_description"), shortDescription);
        },
        "should return error on error when validating": function () {
            var data = {
                name: '',
                facility_type: {
                    id: -1
                },
                unit_type: {
                    id: -1
                },
                unit_name: '',
                capacity: -1,
                contact_person: {
                    phone_number: 'abc'
                }
            };

            var testFacility = new ns.Facility(data);
            testFacility.save();

            Backbone.$ = {
                "ajax": this.stub().yieldsTo("success", {'id': 1234}),
            };

            assert.equals(testFacility.validationError.length, 6);

            // there should NOT have been any attempt to do a save to server, hence id should not have been set.
            assert.equals(testFacility.id, undefined);

        },

        "should return error on error when validating with missing contact_person object": function () {
            var data = {
                name: 'abc',
                facility_type: {
                    id: 1
                },
                unit_type: {
                    id: 1
                },
                unit_name: 'kr',
                capacity: 1
            };

            var testFacility = new ns.Facility(data);
            testFacility.save();

            Backbone.$ = {
                "ajax": this.stub().yieldsTo("success", {'id': 1234}),
            };

            assert.equals(testFacility.validationError.length, 1);

            // there should NOT have been any attempt to do a save to server, hence id should not have been set.
            assert.equals(testFacility.id, undefined);

        },

        "should not return validation errors when saving and trigger save": function () {
            var data = {
                name: 'Min skole',
                facility_type: {
                    id: 1
                },
                unit_type: {
                    id: 1
                },
                unit_name: 'Gymsal',
                capacity: 0,
                contact_person: {
                    phone_number: '12345678'
                }
            };

            Backbone.$ = {
                "ajax": this.stub().yieldsTo("success", {'id': 123})
            };

            var testFacility = new ns.Facility(data);
            testFacility.save();

            assert.equals(testFacility.validationError, null);
            assert.equals(testFacility.id, 123);
        }
    });

}(Flod));
