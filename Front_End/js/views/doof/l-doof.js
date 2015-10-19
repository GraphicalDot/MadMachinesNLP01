'use strict';

define(function (require) {

	var Handlebars = require('handlebars');
	var Marionette = require('backbone.marionette');
	var Template = require('text!./l-doof.html');
	var Radio = require('backbone.radio');

	// Layout Requirement View
	var GoogleMapsView = require('./_googleMaps/i-googleMaps');
	var DataView = require('./_layout/_data/c-data');
	var SearchView = require('./_searchForm/i-searchForm');
	var ChatView= require('./_chat/i-chat');
	var SingleItemView= require('./_singlePickery/i-singlePickery');

	// Menu Items View
	var ShowFeedback = require('./_feedback/i-feedback');
	var HowItWorks = require('./_howItWorks/i-howItWorks');
	var EnterYourQuery = require('./_enterQuery/i-enterQuery');

	return Marionette.LayoutView.extend({

		className: 'row doof-main-row',
		template: Handlebars.compile(Template),

		regions: {
			'search': '.searchFormRow',
			'map': '.google-map-col',
			'grid-item': '.pickeryItemsRow',
			'chat-box': ".b-doof-chat-box",
			'single_details': '.single-item-details-col',
			'modal': '.b-doof-modal'
		},

		initialize: function () {
			var self = this;
			self.lat= 28.5192;
			self.long= 77.2130;

			if (navigator.geolocation) {
				navigator.geolocation.getCurrentPosition(function (position) {
					self.lat= position.coords.latitude;
					self.long= position.coords.longitude;
					self.updateLatLong();
				});
			}

			this.searchView = new SearchView();
			this.googleMapView = new GoogleMapsView({ lat: this.lat, long: this.long });
			this.dataView = new DataView({ lat: this.lat, long: this.long });
			this.chatView= new ChatView();

			this.doofChannel = Radio.channel('doof');

			this.doofChannel.on("feedbackClicked", function () { self.showFeedback() });
			this.doofChannel.on("howItWorksClicked", function () { self.howItWorks() });
			this.doofChannel.on("enterYourQueryClicked", function () { self.enterYourQuery() });

			this.doofChannel.on("updateData", function(data) {self.updateData(data); });
			this.doofChannel.on("loadEmpty", function() {self.loadEmpty()});
			this.doofChannel.on("loadSingleEatery", function(eatery_name, eatery_id) {self.showSingleEatery(eatery_name, eatery_id)});

			this.doofChannel.on("goToLocation", function(location) {self.goToLatLng(location); });

			this.doofChannel.on("feedback", function() {self.showFeedback();});
		},

		updateLatLong: function() {},

		goToLatLng: function(location) {
			console.log(location);
			this.googleMapView.goToLocation(location);
		},

		updateData: function (data) {
			this.dataView.updateData(data);

			this.googleMapView.updateMarkers(data);
			this.googleMapView.updateBound(data);
		},

		loadEmpty: function() {
			this.dataView.refresh();
			this.googleMapView.travelBack();
		},

		onBeforeShow: function () {
			this.showChildView('search', this.searchView);
			this.showChildView('map', this.googleMapView);
			this.showChildView('grid-item', this.dataView);
			this.showChildView('chat-box', this.chatView);
		},

		showFeedback: function () {
			this.showChildView('modal', new ShowFeedback());
		},

		howItWorks: function () {
			this.showChildView('modal', new HowItWorks());
		},

		enterYourQuery: function () {
			this.showChildView('modal', new EnterYourQuery());
		},

		showSingleEatery: function(eatery_name) {
			this.showChildView('single_details', new SingleItemView({eatery_name: eatery_name}));
		}
	});
});