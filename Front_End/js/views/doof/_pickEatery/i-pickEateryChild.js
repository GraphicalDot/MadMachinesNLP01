'use strict';

define(['jquery', 'underscore', 'backbone', 'backbone.marionette', 'text!./pickEateryChild.html', 'views/modifyViewOnEateryView'], function ($, _, Backbone, Marionette, Template, ModifyViewonEatery) {

	return Marionette.ItemView.extend({

		tagName: "tr",

		template: _.template(Template),

		eatery_name: function () { return this.model.eatery_name },
		trending1: function () { return this.model.trending1 },
		trending2: function () { return this.model.trending2 },
		cost: function () { return this.model.cost },
		service: function () { return this.model.service },
		ambience: function () { return this.model.ambience },

		initialize: function(opts) {
			this.model= opts.model;
		},

		onShow: function() {
			// this.$el.append(this.template(this));
			this.$el.attr("lat", this.model.eatery_coordinates[0]);
			this.$el.attr("long", this.model.eatery_coordinates[1]);
			this.$el.attr("eatery_id", this.model.eatery_id);
			this.$el.attr("style", "color: #E9E9E9");
			return this;
		},

		events: {
			"click .eatery-row": 'clicked'
		},

		clicked: function(event) {
			event.preventDefault();
			var subView = new ModifyViewonEatery({"model": {"eatery_id": this.model.eatery_id, "eatery_name": this.model.eatery_name, "eatery_lat": this.model.eatery_coordinates[0], "eatery_lng": this.model.eatery_coordinates[1]}});
			subView.render().el;
		}
	});
});