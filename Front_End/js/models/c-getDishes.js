'use strict';

define(function(require) {
	var Backbone= require('backbone');

	var Dish= Backbone.Model.extend();

	return Backbone.Collection.extend({
		url: window.get_dishes,
		model: Dish,
		parse: function(response) {
			return response.result;
		}
	});
});