'use strict';

define(function(require) {

	var Marionette= require('backbone.marionette');
	// var Masonry= require('masonry');

	var TrendingCollection= require('/js/models/c-trending.js');
	// var GetDishesCollection= require('/js/models/c-getDishes.js');

	var DataChildView= require('./i-data');

	return Marionette.CollectionView.extend({
		initialize: function(opts) {

			this.collection= new TrendingCollection();
			this.oldCollection= this.collection;
			this.collection.fetch({method: 'POST', data: {lat: this.options.lat, lng: this.options.long}});

			this.name= 'dataview';
		},
		childView: DataChildView,
		className: 'row',
		updateData: function(data) {
			this.collection= data;
			this.render();
			console.log(1);
		},
		refresh: function() {
			this.collection= this.oldCollection;
			this.render();
		},
		onShow: function() {
		}
	});
});