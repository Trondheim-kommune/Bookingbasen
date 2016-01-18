(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    var backupBody = undefined;

    var setup = function() {

        var ctxPath = "";
            // There is no contextPath when buster-static is used
            if (buster.env.contextPath !== undefined) {
                ctxPath = buster.env.contextPath;
            }
            var templateUrl = ctxPath + "/form_templates";
            backupBody = document.body;

            $.ajax({
                async: false,
                url: templateUrl,
                success: function (response) {
                    document.body = document.createElement("body");
                    $(document.body).html(response);
                }
            });

        console.log("setup");

    };

    var teardown = function() {
        document.body = backupBody;
        console.log("teardown");
    };

    buster.testCase('FormElementsTest', {

        setUp: function () {
            setup();
        },

        tearDown :  function() {
            teardown();
        },

        "FormSelect should render select": function () {

            var input = new ns.FormElems.FormSelect({
                "id": "test_select",
                "label": "Test Select",
                "options": {
                    "option_1": {"name": "Option 1"},
                    "option_2": {"name": "Option 2", "selected": true}
                }
            }).render();
            assert.equals(input.$("option").length, 3);
            console.log("a");
        },

        "FormSelect should trigger event on change and return right value": function () {
            var input = new ns.FormElems.FormSelect({
                "id": "test_select",
                "label": "Test Select",
                "options": {
                    "option_1": {"name": "Option 1"},
                    "option_2": {"name": "Option 2", "selected": true}
                }
            }).render();

            var spy = this.spy();
            input.on("change", spy);
            assert.equals(input.getValue(), "option_2");
            input.$("select").val("option_1").trigger('change');
            assert.equals(input.getValue(), "option_1");
            assert.called(spy);
        },

        "MinMaxSelect should return min and max of right type": function () {
            var input = new ns.FormElems.MinMaxSelect({
                "id": "test",
                "label": "Test MinMax",
                "options": {
                    "option_1": {"name": "Option 1", "min": 1, "max": 2},
                    "option_2": {"name": "Option 2", "min": 2, "selected": true},
                    "option_3": {"name": "Option 3"}
                }
            }).render();

            var spy = this.spy();
            input.on("change", spy);
            assert.equals(input.getValue(), {"min_test": 2});
            input.$("select").val("option_1").trigger('change');
            assert.equals(input.getValue(), {"min_test": 1, "max_test": 2});
            input.$("select").val("option_3").trigger('change');
            assert.equals(input.getValue(), null);
            assert.calledTwice(spy);
        }
    });

}(Flod));