'use strict';

define(['jquery', 'underscore', 'backbone', 'backbone.marionette', 'text!./pickingEatery.html', 'views/pickEateryChildView', 'tablesorter'], function ($, _, Backbone, Marionette, Template, PickEateryChildView) {

	return Marionette.ItemView.extend({

		initialize: function(options) {
			this.model= options.model;
		},

		template: _.template(Template),

		tagName: 'table',
		idName: 'pickEatery',

		onShow: function() {
			var jqhr = $.post(window.eateries_on_character, {"page_num": self.model.page_num});
			jqhr.done(function(data) {
				if(data.error=== false) {
					$.each(data.results, function(iter, eatery) {
						var subView= new PickEateryChildView({model: eatery});
						self.$("#table-body").append(subView.render().el);
					});
				}

				self.$("#pickEatery").tablesorter();
			});
		}
	});
});