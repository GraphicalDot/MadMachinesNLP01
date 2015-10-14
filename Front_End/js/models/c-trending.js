'use strict';

define(function(require) {

	var _= require('underscore');
	var Backbone= require('backbone');
	var DataModel= require('./trending.js');

	return Backbone.Collection.extend({
		url: window.get_trending,
		// sync: function(method, collection, options) {

		// 	options.method= 'POST';
		// 	options.data= options.data || {};

		// 	options.data.lat= collection.lat;
		// 	options.data.lng= collection.long;

		// 	return Backbone.sync(method, collection, options);
		// },
		parse: function(response) {
			if(response.success) {

				var responseResult= response.result;
				// var categories= Object.keys(responseResult);
				var output= [];

				_.each(["food", "service", "cost", "ambience"], function(category) {
					var categoryResponse= responseResult[category];

					_.each(categoryResponse, function(singleItem) {
						// console.log(singleItem);
						singleItem.category= category;
						output.push(singleItem);
					});
				});

				return output;
			} else {
				return response.error;
			}
		},
		model: DataModel
	});
});