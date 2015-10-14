'use strict';

define(function(require) {

	var Handlebars= require('handlebars');
	var Template= require('text!./howItWorks.html');
	var Marionette= require('backbone.marionette');

	return Marionette.ItemView.extend({
		className: 'modal',
		id: 'feedback-modal',
		template: Handlebars.compile(Template),

		onShow: function() {
			this.$el.openModal();
		}
	})
});