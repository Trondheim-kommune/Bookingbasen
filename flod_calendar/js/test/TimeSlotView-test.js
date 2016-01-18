(function (ns) {
    "use strict";

    var assert = assert || buster.referee.assert;
    var refute = refute || buster.referee.refute;

    buster.testCase('TimeSlotViewTest', {

        "should create a slot element for a TimeSlot": function () {
            var coll = new Backbone.Collection([]);
            coll.options = {slot_duration: 30};
            var data = {
                "start_time": "2013-09-04T17:00:00",
                "end_time": "2013-09-04T18:00:00",
                "person": {"uri": "/persons/1", "name": "Navn Navnesen"},
                "organisation": {"uri": "/oranisations/1", "name": "Org 1"},
                "resource": {"uri": "/resources/1"},
                "status": "Denied"
            };
            var ts = new Flod.TimeSlot(data);
            ts.collection = coll;

            var slotView = new ns.TimeSlotView({"model": ts, "slotDuration": 30}).render();
            assert(slotView.$el.hasClass("slot"));
            assert(slotView.$("div").hasClass("denied"));
            assert.equals(slotView.$("div").attr('title'), "Org 1");
            assert.equals(parseInt(slotView.$el.attr("colspan"), 10), 2);
        },

        "should redraw slot when display_name changed": function () {
            var coll = new Backbone.Collection([]);
            coll.options = {slot_duration: 30};
            var data = {
                "start_time": "2013-09-04T17:00:00",
                "end_time": "2013-09-04T18:00:00",
                "person": new Backbone.Model({"uri": "/persons/1", "name": "Navn Navnesen"}),
                "resource": {"uri": "/resources/1"}
            };
            var ts = new Flod.TimeSlot(data);
            ts.collection = coll;

            var slotView = new ns.TimeSlotView({"model": ts, "slotDuration": 30 }).render();
            assert(slotView.$el.hasClass("slot"));
            assert.equals(slotView.$("div").attr('title'), "Navn Navnesen");

            ts.set("display_name", "Bambus");

            assert.equals(slotView.$("div").attr('title'), "Bambus");
        },

        "should be draggable and resizeable if editable is true": function () {
            var coll = new Backbone.Collection([]);
            coll.options = {slot_duration: 30};
            var data = {
                "start_time": "2013-09-04T17:00:00",
                "end_time": "2013-09-04T18:00:00",
                "person": {"uri": "/persons/1", "name": "Navn Navnesen"},
                "organisation": {"uri": "/oranisations/1", "name": "Org 1"},
                "resource": {"uri": "/resources/1"},
                "status": "Denied",
                "editable": true
            };
            var ts = new Flod.TimeSlot(data);
            ts.collection = coll;

            var slotView = new ns.TimeSlotView({"model": ts, "slotDuration": 30 }).render();
            assert(slotView.$("div").hasClass("ui-draggable"), "should be draggable");
            assert(slotView.$("div").hasClass("ui-resizable"), "should be resizeable");
        },

        "should not be draggable and resizeable if editable is false": function () {
            var coll = new Backbone.Collection([]);
            coll.options = {slot_duration: 30};
            var data = {
                "start_time": "2013-09-04T17:00:00",
                "end_time": "2013-09-04T18:00:00",
                "person": {"uri": "/persons/1", "name": "Navn Navnesen"},
                "organisation": {"uri": "/oranisations/1", "name": "Org 1"},
                "resource": {"uri": "/resources/1"},
                "status": "Denied",
                "editable": false
            };
            var ts = new Flod.TimeSlot(data);
            ts.collection = coll;

            var slotView = new ns.TimeSlotView({"model": ts, "slotDuration": 30 }).render();
            refute(slotView.$("div").hasClass("ui-draggable"), "should not be draggable");
            refute(slotView.$("div").hasClass("ui-resizable"), "should not be resizeable");
        }
    });

}(Flod));