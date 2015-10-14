'use strict';

define(function(require) {

	var Marionette= require('backbone.marionette');
	var Handlebars= require('handlebars');
	var Template= require('text!./chat-box.html');

	return Marionette.ItemView.extend({
		template: Handlebars.compile(Template)
	});

});