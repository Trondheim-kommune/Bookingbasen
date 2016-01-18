var config = module.exports;
var fs = require("fs");

config["Browser tests"] = {
    env: "browser",
    rootPath: "../",
    libs: [
        "lib/underscore-min.js",
        "lib/jquery-1.9.1.min.js",
        "lib/bootstrap.min.js",
        "lib/moment.min.js",
        "lib/*.js"
    ],
    sources: [
        "src/TimeSlot.js",
        "src/TimeSlotView.js",
        "src/*.js"
    ],
    tests: [
        "test/*-test.js"
    ]
};

