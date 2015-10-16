'use strict';

define(function (require) {
	var $ = require('jquery');
	var _ = require('underscore');
	var Backbone = require('backbone');
	var Marionette = require('backbone.marionette');
	var Handlebars = require('handlebars');
	var Template = require('text!./singlePickery.html');
	var GetEatery = require('/js/models/m-getEatery.js');


	return Marionette.ItemView.extend({
		initialize: function (opts) {
			var self = this;
			self.opts = opts;
			this.model = new GetEatery();
			this.name = "singleView";
			this.model.fetch({ method: 'POST', data: { 'eatery_name': opts.eatery_name, type_of_data: 'null' } }).then(function () {
				self.render();
				$('.single-item-details-col').removeClass('hidden').show();
				self.drawD3BubbleGraph();
				// self.drawRadialChart();
			});
		},
		template: Handlebars.compile(Template),
		templateHelpers: function () {
			var self = this;
			return {
				'name': self.opts.eatery_name
			}
		},

		events: {
			'click #detail-close': 'close_details'
		},
		close_details: function (e) {
			e.preventDefault();

			Backbone.history.navigate('application');
			$('.single-item-details-col').addClass('hidden').hide();
			this.destroy();
		},

		drawD3BubbleGraph: function () {
			var model = this.model.toJSON();
			var keys = ['ambience', 'cost', 'food', 'service'];

			_.each(keys, function (key, i) {
				var current_key = key,
					key_data = model.result[current_key];
				require(['d3.bubbleGraph'], function () {
					if (current_key === "food") { //array will come in food case, rest all cases object come in response.
						d3BubbleGraph(key_data, 'food');
					} else {
						var temp_array = [];
						for (var key in key_data) {
							var current_data = key_data[key];
							current_data.name = key;
							temp_array.push(current_data);
						}

						d3BubbleGraph(temp_array, current_key);
					}
				});
			});
		},

		drawRadialChart: function () {
			this.collection.each(function (model) {
				var max_total = 0;
				var currentModel = model.toJSON();
				var chart_categories = currentModel.categories;
				var chart_series = currentModel.series;

				var chart_data = [];

				for (var j = 0; j < chart_categories.length; j++) {
					var single_chart_data_object = {};
					single_chart_data_object.term = chart_categories[j];
					single_chart_data_object.count = 0;
					chart_data.push(single_chart_data_object);
				}

				for (var j = 0; j < chart_series.length; j++) {
					var single_chart_series = chart_series[j];
					var chart_series_name = single_chart_series.name, chart_series_color = single_chart_series.color, chart_series_data = single_chart_series.data;

					for (var k = 0; k < chart_series_data.length; k++) {
						(function (main_obj, name, color, data) {
							main_obj[name] = { count: data, color: color };
							main_obj.count += Number(data);
							if (main_obj.count > max_total) {
								max_total = main_obj.count;
							}
						})(chart_data[k], chart_series_name, chart_series_color, chart_series_data[k]);
					}
				}

				chart_data.sort(function (a, b) {
					return b.count - a.count;
				});
				require(['radialGraph'], function () {
					console.log(currentModel.key);
					radialLineChartD3(chart_data, currentModel.key, max_total);
				});
			});
		},
		onBeforeShow: function () {

			// this.makeD3Chart(self.collection.toJSON());
		}
	});
});