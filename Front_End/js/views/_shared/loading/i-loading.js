'use strict';

define(function(require) {

	var $= require('jquery');
	var Handlebars= require('handlebars');
	var Marionette= require('backbone.marionette');
	var Template= require('text!./i-loading.html');

	return Marionette.ItemView.extend({
		className: 'preloader valign-wrapper animated lightSpeedIn',

		template: Handlebars.compile(Template),

		onClose: function() {
			$(this).el.removeClass('lightSpeedIn').addClass('lightSpeedOut');
		}
	});
});