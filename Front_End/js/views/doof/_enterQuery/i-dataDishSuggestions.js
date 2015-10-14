'use strict';

define(['jquery', 'underscore', 'backbone', 'backbone.marionette', 'text!./dataDishSuggestions.html', 'views/modifyViewOnEateryView'], function ($, _, Backbone, Marionette, Template, ModifyViewOnEatery) {

	return Marionette.ItemView.extend({
		template: _.template(Template),

		className: 'grid-item-dish-suggestions card z-depth-3',

		name: function() {this.model.name},
		positive : function(){ return this.model.positive},
		negative : function(){ return this.model.negative},
		neutral : function(){ return this.model.neutral},
		supernegative : function(){ return this.model.supernegative},
		superpositive : function(){ return this.model.superpositive},
		eatery_name : function(){ return this.model.eatery_name},
		initialize: function(options){
			this.model= options.model;
		},
		onShow: function() {
			this.$el.attr("color", "white");
			return this;
		},
		events: {
			"click .data-click-eatery": "clickEatery"
		},
		clickEatery: function(evt) {
			evt.preventDefault();
			var subView = new ModifyViewOnEatery({"model": {"eatery_id": self.model.eatery_id, "eatery_name": self.model.eatery_name, "eatery_lat": self.model.location.lat, "eatery_lng": self.model.location.lon}});
			subView.render().el;
		}
	});
});