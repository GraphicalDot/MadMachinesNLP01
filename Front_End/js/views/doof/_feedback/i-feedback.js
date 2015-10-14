/* global Materialize */
'use strict';

define(function(require) {

	var Backbone= require('backbone');
	var Handlebars= require('handlebars');
	var Template= require('text!./feedback.html');
	var Marionette= require('backbone.marionette');

	return Marionette.ItemView.extend({
		className: 'modal bottom-sheet',

		id: 'feedback-modal',

		template: Handlebars.compile(Template),

		ui: {
			textarea: 'textarea',
			name: 'input[type="text"]',
			telephone: 'input[type="tel"]',
			email: 'input[type="email"]'
		},

		initialize: function() {
			var FeedbackModel= Backbone.Model.extend({
				url: window.users_feedback
			});
			this.feedbackModel= new FeedbackModel();
		},

		sendFeedback: function() {
			var textareaValue= this.ui.textarea.val();
			var telephoneValue= this.ui.telephone.val();
			var nameValue= this.ui.name.val();
			var emailValue= this.ui.email.val();
			if(textareaValue) {
				var dataObject= {
					feedback: textareaValue,
					telephone: telephoneValue,
					email: emailValue,
					name: nameValue
				};

				this.feedbackModel.fetch({data: dataObject, type: 'POST'}).then(function() {

					Materialize.toast("Feedback successfully submitted", 1000);
				});
			} else {
				Materialize.toast("Feedback cannot be empty >.<", 1000);
			}
		},

		onShow: function() {
			var self= this;
			this.$el.openModal({
				dismissible: true,
				opacity: 0.5,
				in_duration: 300,
				out_duration: 200,
				complete: function() {
					self.sendFeedback();
				}
			});
		}
	})
});