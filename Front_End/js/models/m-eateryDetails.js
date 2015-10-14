'use strict';

define(function (require) {

	var _ = require('underscore');
	var Backbone = require('backbone');

	return Backbone.Model.extend({
		url: window.get_eatery,

		parse: function (response) {
			if (response.success) {

				var responseResult = response.result;
				// var categories= Object.keys(responseResult);
				var output = [];

				_.each(["food", "service", "cost", "ambience"], function (category) {
					var categoryResponse = responseResult[category];

					_.each(categoryResponse, function (singleItem) {
						singleItem.category = category;
						output.push(singleItem);
					});
				});

				return output;
			} else {
				return response.error;
			}
		}
	});
});