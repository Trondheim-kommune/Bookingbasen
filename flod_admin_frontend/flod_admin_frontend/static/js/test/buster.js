var config = module.exports;

config["Browser tests"] = {
    env: "browser",
    rootPath: "../",
    libs: [
        "lib/jquery-1.9.1.min.js",
        "lib/underscore-min.js",
        "lib/backbone-min.js",
        "lib/jquery-ui-1.10.3.custom.min.js",
        "lib/moment.min.js",
        "lib/leaflet/leaflet.js",
        "lib/*.js"
    ],
    sources: [
        "src/SimpleApplication.js",
        "src/calendar_extensions.js",
        "src/ApplicationCalendar.js",
        "src/BookingForActorCalendar.js",
        "src/facility_page/FacilityGeocoding.js",
        "src/Facility.js",
        "src/facility_page/FacilityImageMainView.js",
        "src/facility_page/FacilityDocumentsMainView.js",
        "src/RentalTypesView.js",
        "src/facility_page/FacilityBlockedTimeView.js",
        "src/facility_page/FacilityAdministratorView.js",
        "src/facility_page/FacilityInternalNotes.js",
        "src/facility_page/FacilityMainPage.js",
        "src/**/*.js"
    ],
    tests: [
        "test/*-test.js"
    ]
};
