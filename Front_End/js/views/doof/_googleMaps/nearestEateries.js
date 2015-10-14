define(function(require) {

	var Backbone= require('backbone');

	var SingleEatery= Backbone.Model.extend({});

	var NearestEateries= Backbone.Collection.extend({
		model: SingleEatery,
		url: window.nearest_eateries,
		parse: function(response) {
			return response.result;
		}
	});

	return NearestEateries;
});