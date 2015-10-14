'use strict';

define(function(require) {

	var Backbone= require('backbone');

	return Backbone.Model.extend({
		url: window.nearest_eateries,
		// sync: function(method, model, options) {
		// 	options.data= {
		// 		lat: model.lat,
		// 		long: model.long,
		// 		range: 10
		// 	};

		// 	options.method= 'POST';
		// 	return Backbone.sync(method, model, options);
		// },
		parse: function(response) {
			return response.result;
		}
	});
});