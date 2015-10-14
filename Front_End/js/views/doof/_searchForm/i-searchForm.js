'use strict';

define(function(require) {

	var $= require('jquery');
	var Handlebars= require('handlebars');
	var Marionette= require('backbone.marionette');
	var Radio = require('backbone.radio');
	var Template= require('text!./i-searchForm.html');

	var GetDishesCollection= require('js/models/c-getDishes.js');

	return Marionette.ItemView.extend({

		className: 'row',
		template: Handlebars.compile(Template),

		initialize: function() {

			this.doofChannel = Radio.channel('doof');
			this.dishes= new GetDishesCollection();
		},

		onShow: function() {
			var self= this;
			require(['typeahead'], function() {
				$('#search-dish').typeahead(
					{ hint: true, highlight: true, minLength: 4 },
					{ limit: 12, async: true,
						select: function (event, name) {
							console.log(name)
						},
						source: function (query, processSync, processAsync) {
							return $.ajax({
								url: window.get_dish_suggestions,
								type: 'GET',
								data: { query: query },
								dataType: 'json',
								success: function (json) {
									return processAsync(json.options);
								}
							});
						}
					}
				);

				function onDishSelect(dishName) {
					if(dishName) {
						self.dishes.fetch({method: 'POST', data: {"dish_name": dishName}}).then(function() {
							self.doofChannel.trigger("updateData", self.dishes);
						});
					} else {
						self.doofChannel.trigger("loadEmpty");
					}
				}

				$("#search-dish").enterKey(function () {
					var dish_name = $(this).val();
					onDishSelect(dish_name);
				})

				$('#search-dish').bind('typeahead:select', function (ev, suggestion) {
					var dish_name = $(this).val();
					onDishSelect(dish_name);
				});


				$('#search-eatery').typeahead(
					{ hint: true, highlight: true, minLength: 2 },
					{ limit: 12, async: true,
						source: function (query, processSync, processAsync) {
							return $.ajax({
								url: window.get_eatery_suggestions,
								type: 'GET',
								data: { query: query },
								dataType: 'json',
								success: function (json) {
									return processAsync(json.options);
								}
							});
						}
					}
				);

				function onEaterySelect(eatery_name) {
					self.doofChannel.trigger("loadSingleEatery", eatery_name);
				}

				$("#search-eatery").enterKey(function () {
					var eatery_name = $(this).val();
					onEaterySelect(eatery_name);
				});

				$('#search-eatery').bind('typeahead:select', function (ev, suggestion) {
					var eatery_name = $(this).val();
					onEaterySelect(eatery_name);
				});
			});
		}
	});
});