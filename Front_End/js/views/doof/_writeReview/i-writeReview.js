'use strict';

define(['jquery', 'underscore', 'backbone', 'backbone.marionette', 'text!./writeReview.html', './i-writeReviewChild'], function ($, _, Backbone, Marionette, Template, WriteReviewChild) {

	return Marionette.ItemView.extend({
		template: _.template(Template),

		className: "grid-item-new  card #222930 blue-grey darken-4 z-depth-3",

		eatery_name : function(){ return this.model.eatery_name},
		eatery_id: function(){ return this.model.eatery_id},
		initialize: function(options){
				this.model = options.model;
		},
		render: function(){
			// this.$el.append(this.template(this));
			this.$el.attr("eatery_id", this.model.eatery_id);
			this.$el.attr("style", "text-align: center");
			return this;
		},

		events: {
			"click .write-review": "writeReviewfunction"
		},

		writeReviewfunction: function(event){
			var self = this;
			event.preventDefault();
			console.log("Write review has been clicked with" + this.model.eatery_id);
			var subView = new WriteReviewChild({"model": {"eatery_id": this.model.eatery_id, "eatery_name": this.model.eatery_name}})
			$("body").append(subView.render().el);
			$('.modal-trigger').leanModal({
					dismissible: true, // Modal can be dismissed by clicking outside of the modal
					opacity: .5, // Opacity of modal background
					ready: function() {
							console.log($("modal32").attr("eatery_id"))
						$("#modal32 label").text("write review for" + self.model.eatery_name);
							alert('Ready');


					}, // Callback for Modal open
					complete: function() {

					} // Callback for Modal close
				}
				);
			$("#modal32").openModal();
		}
	});
});