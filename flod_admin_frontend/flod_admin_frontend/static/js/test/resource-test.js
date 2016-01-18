(function (ns) {
    "use strict";
    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;
    buster.testCase('Resource', {
        "should be defined": function () {
            assert(ns.Resource);
        },

        "should have three types of rental": function () {
            var response = {
                "id": 1,
                "auto_approval_allowed": false,
                "single_booking_allowed": true,
                "repeating_booking_allowed": false
            };
            
            Backbone.$ = {
                "ajax": this.stub().yieldsTo("success", response)
            };
            
            var blocked = new ns.Resource( {id: "1" });
            blocked.fetch();

            assert.calledOnce(Backbone.$.ajax);
            assert.equals(blocked.get("id"), 1);
            assert.equals(blocked.get("auto_approval_allowed"), false);
            assert.equals(blocked.get("single_booking_allowed"), true);
            assert.equals(blocked.get("repeating_booking_allowed"), false);
        }
    });
}(Flod));
