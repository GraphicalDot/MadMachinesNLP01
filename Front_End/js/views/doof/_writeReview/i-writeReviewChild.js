'use strict';

define(['jquery', 'underscore', 'backbone', 'backbone.marionette', 'text!./writeReviewChild.html'], function ($, _, Backbone, Marionette, Template) {

	return Marionette.ItemView.extend({
		template: _.template(Template),

		className: "modal-trigger modal #222930 blue-grey darken-4",

		eatery_name: function(){ return this.model.eatery_name},

		initialize: function(options){ this.model = options.model; },

		onShow: function(){
			// this.$el.append(this.template(this));
			this.$el.attr("id", "modal32");
			this.$el.attr("eatery_id", this.model.eatery_id);
			return this;
		},
		submitReview: function(event){
			event.preventDefault();
			$("#modal32").closeModal();
		}
	});
});