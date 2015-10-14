'use strict';

define(function(require) {

	var _= require('underscore');
	var Backbone= require('backbone');

	var Eatery= Backbone.Model.extend();

	return Backbone.Collection.extend({
		url: window.get_eatery,
			parse: function(response) {
				if(response.success) {
					var responseResult= response.result;
					// var categories= Object.keys(responseResult);
					var output= [];

					_.each(["food", "service", "cost", "ambience"], function(category) {
						var categoryResponse= responseResult[category];

						output.push({categories: categoryResponse.categories, series: categoryResponse.series, key: category});
					});
					return output;
				} else {
					return response.error;
				}
			},
		model: Eatery
	});
});