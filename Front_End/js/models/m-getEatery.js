'use strict';

define(function (require) {

	var Backbone = require('backbone');

	var Eatery = Backbone.Model.extend({
		url: window.get_eatery
	});

	return Eatery;
});