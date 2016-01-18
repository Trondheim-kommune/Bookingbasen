var Flod = window.Flod || {};
Flod.FormElems = {};

(function (ns, undefined) {
    "use strict";
    ns.FormElement = Backbone.View.extend({

        isSearchParam: true,

        tagName: "fieldset",

        render: function () {
            this.$el.html("");
            this.$el.append("<label>" + this.options.label + "</label>");
            this.$el.append(this.createInput());
            return this;
        },

        createInput: function () {
            return "";
        },

        getValue: function () {
            return null;
        }
    });

    ns.FormInput = ns.FormElement.extend({

        events: {
            "keyup input": "keyup"
        },

        initialize: function () {
            _.bindAll(this, "keyup");
        },

        createInput: function () {
            return _.template($("#input_template").html(), {"id": this.options.id, placeholder: this.options.placeholder});
        },

        keyup: function () {
            this.trigger("change");
        },

        getValue: function () {
            return this.$el.find("input").val();
        }
    });

    ns.FormSelect = ns.FormElement.extend({

        events: {
            "change select": "change"
        },

        initialize: function () {
            _.bindAll(this, "change");
        },

        createInput: function () {
            var el = $("<select id='" + this.options.id + "'></select>");
            var options = _.map(this.options.options, function (option, key) {
                return _.template($("#option_template").html(), {"key": key, "name": option.name, "selected": option.selected});
            });
            options.unshift(_.template($("#option_template").html(), {"key": "", "name": "---", "selected": false}));
            el.append(options);
            return el;
        },

        change: function () {
            this.trigger("change");
        },

        getValue: function () {
            return this.$("select").val();
        }
    });

    ns.MinMaxSelect = ns.FormSelect.extend({

        createInput: function () {
            var el = $("<select id='" + this.options.id + "'></select>");
            var options = _.map(this.options.options, function (option, key) {
                return _.template($("#option_template").html(), {
                    "key": key,
                    "name": option.name,
                    "selected": option.selected
                });
            });
            el.append(options);
            return el;
        },

        getValue: function () {
            var selected = this.options.options[this.$el.find("select").val()];
            var res = {};
            var id = this.options.id;
            if (selected.max) {
                res["max_" + id] = selected.max;
            }
            if (selected.min) {
                res["min_" + id] = selected.min;
            }
            return (_.isEmpty(res)) ? null : res;
        }
    });

    ns.FormBboxSelect = ns.FormElement.extend({

        events: {
            "change select": "change"
        },

        initialize: function () {
            _.bindAll(this, "change");
        },

        isSearchParam: false,

        createInput: function () {
            var el = $("<select id='" + this.options.id + "'></select>");
            var options = _.map(this.options.options, function (option, key) {
                return _.template($("#option_template").html(), {
                    "key": key,
                    "name": option.name,
                    "selected": option.selected
                });
            });
            el.append(options);
            return el;
        },

        change: function () {
            this.trigger(
                "change",
                {"bbox": this.getValue(true), "id": this.options.id}
            );
        },

        selectOption: function (id) {
            this.$el.find("select").val(id);
        },

        getValue: function (getAll) {
            var val =  this.$el.find("select").val();
            if (this.options.options[val].all && !getAll) {
                return null;
            }
            var geom = this.options.options[val].geometry;
            return {"bbox": geom.getBounds(), "district": val};
        },

        setOptions: function (options) {
            this.options.options = options;
        }
    });

    ns.CheckBoxGroup = ns.FormElement.extend({

        events: {
            "change input": "change"
        },

        initialize: function () {
            _.bindAll(this, "change");
        },

        createInput: function () {
            return _.map(this.options.checkboxes, function (checkbox) {
                return _.template($("#checkbox_group_template").html(), checkbox);
            });
        },

        change: function () {
            this.trigger("change");
        },

        getValue: function () {
            return _.reduce(this.options.checkboxes, function (result, checkbox) {
                result[checkbox.id] = this.$el.find("#" + checkbox.id).is(':checked');
                return result;
            }, {}, this);
        }
    });

    ns.DateSelect = ns.FormElement.extend({

        template: $("#date_select_template").html(),

        events: {
            "change input[name='repeatingRadios']": "toggle"
        },

        initialize: function () {
            this.date = moment();
            this.repeating = false;
            _.bindAll(this, "toggle");
        },

        toggle: function (e) {
            this.repeating = Boolean(parseInt($(e.currentTarget).val(), 10));
            if (this.repeating) {
                this.$(".horizontal").hide();
            } else {
                this.$(".horizontal").show();
            }
        },

        render: function () {
            this.$el.html(_.template(this.template, {"date": this.date.format("DD.MM.YYYY")}));

            this.$('#date_btn').datepicker()
                .on('changeDate', _.bind(function (ev) {
                    this.updateDate(ev.date);
                    this.$('#date_btn').datepicker('hide');
                }, this));
            return this;
        },

        updateDate: function (date) {
            this.date = moment(date);
            this.$("#date").html(this.date.format("DD.MM.YYYY"));
        },

        getValue: function () {
            if (!this.repeating) {
                return this.date.format();
            }
            return null;
        }

    });

}(Flod.FormElems));