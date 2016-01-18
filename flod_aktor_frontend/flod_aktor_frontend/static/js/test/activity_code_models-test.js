(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('StrotimeBookingViewTest', {

        setUp: function () {
            this.brreg_activity_codes = [
                {"flod_activity_types": [{"id": 37, "name": "Dans"}, {"id": 38, "name": "Festival"}, {"id": 39, "name": "Film/multimedia"}, {"id": 40, "name": "Historielag"}, {"id": 41, "name": "Hobby"}, {"id": 42, "name": "Husflid"}, {"id": 43, "name": "Kor"}, {"id": 44, "name": "Kulturminnevern"}, {"id": 45, "name": "Kunst"}, {"id": 46, "name": "Kurs/oppl\u00e6ring"}, {"id": 47, "name": "Litteratur"}, {"id": 48, "name": "Musikk/sang"}, {"id": 49, "name": "Scenekunst"}, {"id": 50, "name": "Skolekorps"}, {"id": 51, "name": "Ungdoms/voksenkorps"}], "code": "1 100", "description": "Kunst og kultur"},
                {"flod_activity_types": [{"id": 1, "name": "Aking, bob, skeleton"}, {"id": 2, "name": "Allidrett"}, {"id": 3, "name": "Amerikansk idrett"}, {"id": 4, "name": "Badmington"}, {"id": 5, "name": "Bandy"}, {"id": 6, "name": "Basketball"}, {"id": 7, "name": "Bedriftsidrett"}, {"id": 8, "name": "Biljard"}, {"id": 9, "name": "Boksing"}, {"id": 10, "name": "Bordtennis"}, {"id": 11, "name": "Bowling"}, {"id": 12, "name": "Bryting"}, {"id": 13, "name": "Bueskyting"}, {"id": 14, "name": "Casting"}, {"id": 15, "name": "Cheerleading"}, {"id": 16, "name": "Cricket"}, {"id": 17, "name": "Curling"}, {"id": 18, "name": "Dans"}, {"id": 19, "name": "Fekting"}, {"id": 20, "name": "Fotball"}, {"id": 21, "name": "Friidrett"}, {"id": 22, "name": "H\u00e5ndball"}, {"id": 23, "name": "Ishockey"}, {"id": 24, "name": "Judo"}, {"id": 25, "name": "Kampsport"}, {"id": 26, "name": "Kickboksing"}, {"id": 27, "name": "Langrenn, hopp"}, {"id": 28, "name": "Orientering"}, {"id": 29, "name": "Skiskyting"}, {"id": 30, "name": "Sk\u00f8ytesport"}, {"id": 31, "name": "Softball og baseball"}, {"id": 32, "name": "Sv\u00f8mming"}, {"id": 33, "name": "Sykling"}, {"id": 34, "name": "Tennis"}, {"id": 35, "name": "Turn"}, {"id": 36, "name": "Volleyball"}], "code": "1 200", "description": "Idrett"},
                {"flod_activity_types": [], "code": "1 300", "description": "Rekreasjon og sosiale foreninger"},
                {"flod_activity_types": [], "code": "10 100", "description": "Tros- og livssynsorganisasjoner"},
                {"flod_activity_types": [], "code": "11 100", "description": "N\u00e6ringslivs- og arbeidsgiverorganisasjoner"},
                {"flod_activity_types": [], "code": "11 200", "description": "Yrkessammenslutninger"},
                {"flod_activity_types": [], "code": "11 300", "description": "Arbeidstakerorganisasjoner"},
                {"flod_activity_types": [], "code": "12 100", "description": "Andre"},
                {"flod_activity_types": [], "code": "13 100", "description": "Barne- og ungdomsorganisasjoner"},
                {"flod_activity_types": [], "code": "14 100", "description": "Mangfold og inkludering"},
                {"flod_activity_types": [], "code": "2 100", "description": "Grunn- og videreg\u00e5ende utdanning"},
                {"flod_activity_types": [], "code": "2 200", "description": "H\u00f8gskole og universitet"},
                {"flod_activity_types": [], "code": "2 300", "description": "Annen utdanning"},
                {"flod_activity_types": [], "code": "2 400", "description": "Andre helsetjenester"},
                {"flod_activity_types": [], "code": "3 100", "description": "Sykehus og rehabilitering"},
                {"flod_activity_types": [], "code": "3 200", "description": "Sykehjem"},
                {"flod_activity_types": [], "code": "3 300", "description": "Psykiatriske institusjoner"},
                {"flod_activity_types": [], "code": "3 400", "description": "Andre helsetjenester"},
                {"flod_activity_types": [], "code": "4 100", "description": "Sosiale tjenester"},
                {"flod_activity_types": [], "code": "4 200", "description": "Krisehjelp og st\u00f8ttearbeid"},
                {"flod_activity_types": [], "code": "4 300", "description": "\u00d8konomisk og materiell st\u00f8tte"},
                {"flod_activity_types": [], "code": "5 100", "description": "Natur- og milj\u00f8vern"},
                {"flod_activity_types": [], "code": "5 200", "description": "Dyrevern"},
                {"flod_activity_types": [], "code": "6 100", "description": "Lokalsamfunnsutvikling"},
                {"flod_activity_types": [], "code": "6 200", "description": "Bolig- og lokalmilj\u00f8"},
                {"flod_activity_types": [], "code": "6 300", "description": "Arbeidsoppl\u00e6ring"},
                {"flod_activity_types": [], "code": "7 100", "description": "Interesseorganisasjoner"},
                {"flod_activity_types": [], "code": "7 200", "description": "Juridisk r\u00e5dgivning"},
                {"flod_activity_types": [], "code": "7 300", "description": "Politiske organisasjoner"},
                {"flod_activity_types": [], "code": "8 100", "description": "Pengeutdelende stiftelser"},
                {"flod_activity_types": [], "code": "8 200", "description": "Frivillighetssentraler"},
                {"flod_activity_types": [], "code": "9 100", "description": "Internasjonale organisasjoner"}];
        },

        "Flod.BrregActivityCodes should be defined": function () {
            assert(ns.BrregActivityCodes);
        },

        "Flod.ActivityTypes should be defined": function () {
            assert(ns.ActivityTypes);
        },

        "Flod.BrregActivityCodes should be populated when initing with a dict": function () {
            var activityCodes = new ns.BrregActivityCodes(this.brreg_activity_codes);
            assert.equals(activityCodes.length, 32);
        },

        "a Flod.BrregActivityCodes collection should have a Flod.ActivityTypes subcollection": function () {
            var activityCodes = new ns.BrregActivityCodes(this.brreg_activity_codes);
            var code1 = activityCodes.at(0);
            assert(code1.get("flod_activity_types") instanceof ns.ActivityTypes);
        },

        "should be able to get a single BrregActivityCode from BrregActivityCodes": function () {
            var activityCodes = new ns.BrregActivityCodes(this.brreg_activity_codes);
            var selected = activityCodes.getByCodes(["1 300"]);
            assert.equals(selected.length, 1);
            assert(selected instanceof ns.BrregActivityCodes);
        },

        "should be able to get several  BrregActivityCodes from BrregActivityCodes": function () {
            var activityCodes = new ns.BrregActivityCodes(this.brreg_activity_codes);
            var selected = activityCodes.getByCodes(["1 300", "9 100"]);
            assert.equals(selected.length, 2);
            assert(selected instanceof ns.BrregActivityCodes);
        },

        "should be able to get the activity types for all BrregActivityCodes": function () {
            var activityCodes = new ns.BrregActivityCodes(this.brreg_activity_codes);
            var activityTypes = activityCodes.getActivityTypes();

            assert.equals(activityTypes.length, 51);
            assert(activityTypes instanceof ns.ActivityTypes);
        },

        "filtering should give the correct number of types": function () {
            var activityCodes = new ns.BrregActivityCodes(this.brreg_activity_codes).getByCodes(["1 200", "9 100"]);
            var activityTypes = activityCodes.getActivityTypes();
            assert.equals(activityTypes.length, 36);
            assert(activityTypes instanceof ns.ActivityTypes);
        },

        "should be able to get the activity types for all BrregActivityCodes and keep the order": function () {
            var activityCodes = new ns.BrregActivityCodes(this.brreg_activity_codes);
            var activityTypes = activityCodes.getActivityTypes();

            assert.equals(activityTypes.at(0).get("name"), "Dans");
            assert.equals(activityTypes.at(50).get("name"), "Volleyball");
        },

        "BrregActivityCodes should have a toDisplay method": function () {
            var activityCodes = new ns.BrregActivityCodes(this.brreg_activity_codes).getByCodes(["1 200", "9 100"]);
            var displayStrings = activityCodes.toDisplay();
            assert.equals(displayStrings.length, 2);

            assert.equals(displayStrings[0], "Idrett (1 200)");
        }

    });

}(Flod));