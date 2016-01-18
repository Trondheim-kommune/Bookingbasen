var config = module.exports;
var fs = require("fs");

config["Browser tests"] = {
    env: "browser",
    rootPath: "../",
    libs: [
        "lib/underscore-min.js",
        "lib/jquery-1.9.1.min.js",
        "lib/bootstrap.min.js",
        "lib/backbone-min.js",
        "lib/moment.min.js",
        "lib/moment-nb.js",
        "lib/*.js"
    ],
    sources: [
        "src/form_elements.js",
        "src/*.js"
    ],
    tests: [
        "test/*-test.js"
    ],
    resources: [
        {
            path: "/form_templates",
            content: fs.readFileSync('fixtures/form_templates.html', {encoding: "utf-8"})
        }
    ]
};

