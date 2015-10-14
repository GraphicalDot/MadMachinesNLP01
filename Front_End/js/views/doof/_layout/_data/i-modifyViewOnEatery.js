'use strict';

// define(function(require) {

// 	var Marionette= require('backbone.marionette');
// 	var Handlebars= require('handlebars');
// 	var Template= require('text!templates/_authorized/pickingEatery.html');

// 	return Marionette.ItemView.extend({
// 		template: Handlebars.compile(Template),

// 		onShow: function() {
// 			var self= this, range= 10;

// 			// var s
// 		}
// 	})
// });

define(['jquery', 'underscore', 'backbone', 'backbone.marionette'], function ($, _, Backbone, Marionette) {

	return Marionette.ItemView.extend({
		// template: _.template(Template),

		initialize: function(options) {
			this.model= options.model;
		},

		// onShow: function() {
		// 	var self= this, range= 10;
		// 	var subView=  new EateryDetails({"model": {"eatery_id": this.model.eatery_id, "eatery_name": this.model.eatery_name}});

		// 	var jqhr = $.post(window.nearest_eateries, {"lat": this.model.eatery_lat, "long": this.model.eatery_lng, "range": range});
		// 	jqhr.done(function(data) {
		// 		if(data.error=== false) {
		// 			reloadGoogleMap(self.model.eatery_lat, self.model.eatery_lng, data.result);
		// 		} else {
		// 			var subView= new ErrorView();
		// 			$(".trending-bar-chart").html(subView.render().el);
		// 		}
		// 	});

		// 	jqhr.fail(function(data) {
		// 		var subView = new ErrorView();
		// 		$(".dynamic-display").html(subView.render().el);
		// 	});

		// 	var jqhr2 = $.post(window.get_trending, {"lat": this.model.eatery_lat, "lng": this.model.eatery_lng});
		// 	jqhr2.done(function(data){
		// 		if(data.error=== false) {
		// 			$(".grid-grid").html("");
		// 			$(".grid-grid").append('<div class="grid-item-new card z-depth-3"> <p>Trending </p><p>near</p><p>' + self.model.eatery_name + '</p>');

		// 			var subView = new WriteReview({"model": {"eatery_id": self.model.eatery_id, "eatery_name": self.model.eatery_name}});
		// 			$(".grid-grid").append(subView.render().el);

		// 			$.each(["food", "service", "cost", "ambience"], function(iter, category){
		// 				$.each(data.result[category], function(iter2, model){
		// 					model["category"] = category;
		// 					var subview = new DataView({model: model});
		// 					$(".grid-grid").append(subview.render().el);
		// 				});
		// 			});

		// 			$(".grid-grid").gridalicious(
		// 				{ 	selector: '.grid-item-new', gutter: 1, width: 200, animate: true,
		// 						animationOptions: { queue: true, speed: 200, duration: 300, effect: 'fadeInOnAppear'
		// 				}

		// 			});
		// 		} else {
		// 			var subView = new ErrorView();
		// 			$(".trending-bar-chart").html(subView.render().el);
		// 		}
		// 	});
		// 	return this;
		// }
	});
});