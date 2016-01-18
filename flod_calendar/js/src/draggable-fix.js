$.widget("ui.draggable", $.extend({}, $.ui.draggable.prototype, {
    _setContainment: function () {
        "use strict";
        var over, c, ce,
            o = this.options;

        c = $(o.containment);
        ce = c[0];

        if (!ce) {
            return;
        }

        over = c.css("overflow") !== "hidden";

        var offset_left = c.children().first().children().first().width();

        this.containment = [
            (parseInt(c.css("borderLeftWidth"), 10) || 0) + (parseInt(c.css("paddingLeft"), 10) || 0) + offset_left,
            (parseInt(c.css("borderTopWidth"), 10) || 0) + (parseInt(c.css("paddingTop"), 10) || 0),
            (over ? Math.max(ce.scrollWidth, ce.offsetWidth) : ce.offsetWidth) - (parseInt(c.css("borderRightWidth"), 10) || 0) - (parseInt(c.css("paddingRight"), 10) || 0) - this.helperProportions.width - this.margins.left - this.margins.right,
            (over ? Math.max(ce.scrollHeight, ce.offsetHeight) : ce.offsetHeight) - (parseInt(c.css("borderBottomWidth"), 10) || 0) - (parseInt(c.css("paddingBottom"), 10) || 0) - this.helperProportions.height - this.margins.top  - this.margins.bottom
        ];
        this.relative_container = c;
    }
}));