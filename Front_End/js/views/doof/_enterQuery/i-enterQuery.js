/* global Materialize */
'use strict';

define(function(require) {

	var $= require('jquery');
	var Backbone= require('backbone');
	var Handlebars= require('handlebars');
	var Template= require('text!./enterYourQuery.html');
	var Marionette= require('backbone.marionette');

	return Marionette.ItemView.extend({
		className: 'modal',
		id: 'feedback-modal',
		template: Handlebars.compile(Template),

		initialize: function() {
			var ResolveQueryModel= Backbone.Model.extend({
				url: window.resolve_query
			});
			this.resolveQueryModel= new ResolveQueryModel();
		},

		ui: {
			textarea: 'textarea'
		},

		query_submitted: function() {
			var self= this;
			var queryValue =this.ui.textarea.val();
			if(queryValue && queryValue.length) {
				Materialize.toast("Please wait while we process your query.");

				this.resolveQueryModel.fetch({data: {text: queryValue}, type: 'POST'}).then(function() {
					console.log(self.resolveQueryModel);
				});
			} else {
				Materialize.toast("Please write something to let us, help you find awesomeoness", 2000, "rounded");
			}
		},

		onShow: function() {
			var self= this;

			this.$el.openModal({
				complete: function() {
					self.query_submitted();
				}
			});
		}
	})
});