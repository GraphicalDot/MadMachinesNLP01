'use strict';

define(function(require) {

	var Handlebars= require('handlebars');
	var Marionette= require('backbone.marionette');
	var Radio= require('backbone.radio');
	var Template= require('text!./i-data.html');
	var ModifyViewOnEatery= require('./i-modifyViewOnEatery');

	return Marionette.ItemView.extend({
		template: Handlebars.compile(Template),

		className: "grid-item-new col s12 m6 l4",
		templateHelpers: {
			itemname: function() {
				var category= this.category;
				if(category!== 'food') {
					return 'Trending '+ category;
				} else {
					return this.name;
				}
			}
		},
		category: function () { return this.model.category },
		positive: function () { return this.model.positive },
		negative: function () { return this.model.negative },
		neutral: function () { return this.model.neutral },
		supernegative: function () { return this.model.supernegative },
		superpositive: function () { return this.model.superpositive },
		eatery_name: function () { return this.model.eatery_name },
		initialize: function (options) {
			this.model = options.model;
			this.doofChannel = Radio.channel('doof');
		},
		onShow: function() {
			this.$el.attr("color", "white");
		},
		events: {
			"click .data-click-eatery": "clickEatery",
			'click .card-show-on-map': 'showLocation',
			'click .explore-pickery': 'explorePickery'
		},

		showLocation: function(e) {
			e.preventDefault();

			this.doofChannel.trigger('goToLocation', this.model.get('location'));
		},
		explorePickery: function(e) {
			$(".single-item-details-col").removeClass('offset-s6');
		},
		clickEatery: function(evt) {
			evt.preventDefault();
			var subView = new ModifyViewOnEatery({"model": {"eatery_id": self.model.eatery_id, "eatery_name": self.model.eatery_name, "eatery_lat": self.model.location.lat, "eatery_lng": self.model.location.lon}});
			subView.render().el
		}
	});
});