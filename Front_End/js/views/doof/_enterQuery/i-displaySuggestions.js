'use strict';

define(['jquery', 'underscore', 'backbone', 'backbone.marionette'], function ($, _, Backbone, Marionette) {

	return Marionette.ItemView.extend({
		// template: _.template(Template),

		initialize: function(options) {
			// this.model = options.model;
			// var appRadioChannel= Backbone.Radio.channel('appChannel');
			// vent.on('remove-suggestion', this.removeSuggestion, this);
		}
	});
});