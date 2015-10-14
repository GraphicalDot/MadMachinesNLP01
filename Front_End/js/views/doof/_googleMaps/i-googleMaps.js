/* global google */
'use strict';

define(function(require) {

	var $= require('jquery');
	var _= require('underscore');
	var Handlebars= require('handlebars');
	var Marionette= require('backbone.marionette');
	var Radio= require('backbone.radio');

	var NearestEateries= require('./nearestEateries');

	return Marionette.ItemView.extend({

		id: 'googleMap',
		template: Handlebars.compile(""),

		initialize: function() {
			this.lat= this.options.lat ? this.options.lat : 21;
			this.long= this.options.long ? this.options.long : 78;

			this.collection= new NearestEateries();
			this.oldCollection= this.collection;
			this.collection.fetch({method: 'POST', data: {lat: this.lat, long: this.long, range: 10}});
			this.markersArray= [];

			this.doofChannel = Radio.channel('doof');
		},

		showMarkers: function(data) {
			var self= this;

			_.each(this.markersArray, function(currentMarker) {
				currentMarker.setMap(null);
			});
			this.markersArray= [];

			var bounds = new google.maps.LatLngBounds();
			this.collection.each(function(marker_model) {
			// _.each(this.model, function(marker) {
				var marker= marker_model.toJSON();


				var markerLat= "", markerLong= "";
				if(marker.eatery_coordinates) {
					markerLat= marker.eatery_coordinates[0];
					markerLong= marker.eatery_coordinates[1];
				} else {
					markerLat= marker.location.lat;
					markerLong= marker.location.lon;
				}

				var mapMarker= new google.maps.Marker({
					map: self.map,
					position: new google.maps.LatLng(markerLat, markerLong),
					title: marker.eatery_name,
					eatery_id: marker.eatery_id,
					address: marker.eatery_address ? marker.eatery_address : "Not defined..",
					html: "<div id='infobox'>"+ marker.eatery_name+ "<br />"+ marker.eatery_address+ "</div>"
				});

				google.maps.event.addListener(mapMarker, 'mouseover', function() {
					self.infoWindow.setContent(this.get('html'));
					self.infoWindow.open(self.map, this);
				});

				google.maps.event.addListener(mapMarker, 'mouseout', function() {
					self.infoWindow.close();
				});

				google.maps.event.addListener(mapMarker, 'click', function() {
					$(".single-item-details-col").addClass('offset-s6');
					console.log(this.get('eatery_name'));
						self.doofChannel.trigger('loadSingleEatery', marker.eatery_name, marker.eatery_id);
					// var subView= new EateryDetail({model: {"eatery_id": this.get("eatery_id"), "eatery_name": this.get("eatery_name")}});

				});

				self.markersArray.push(mapMarker);

				if(markerLat && markerLong) {
					bounds.extend(new google.maps.LatLng(markerLat, markerLong));
				}
			});

			self.map.fitBounds(bounds);

			google.maps.event.addListener(self.map, 'click', function(event) {
				// var lat= event.latLng.lat(), lng= event.latLng.lng();
				// self.render();
			});
		},

		updateMarkers: function(data) {
			this.collection= data;
			this.showMarkers();
		},

		travelBack: function() {
			this.collection= this.oldCollection;
			this.showMarkers();
		},

		goToLocation: function(location) {
			var self= this;
			require(['require-async!http://maps.google.com/maps/api/js?sensor=false'], function() {
				var latLng= new google.maps.LatLng(location.lat, location.lon);
				self.map.panTo(latLng);
			});
		},

		updateBound: function() {

		},

		onShow: function() {
			var self= this;
			require(['require-async!http://maps.google.com/maps/api/js?sensor=false'], function() {
				var mapCanvas= document.getElementById('googleMap');
				var mapOptions= {
						center: new google.maps.LatLng(self.lat, self.long),
						zoom: 19,
						mapTypeId: google.maps.MapTypeId.ROADMAP,
						draggable: true,
						scrollwheel: false,
						// styles: [{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#6195a0"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"landscape","elementType":"geometry.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"poi.park","elementType":"geometry.fill","stylers":[{"color":"#e6f3d6"},{"visibility":"on"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45},{"visibility":"simplified"}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#f4d2c5"},{"visibility":"simplified"}]},{"featureType":"road.highway","elementType":"labels.text","stylers":[{"color":"#4e4e4e"}]},{"featureType":"road.arterial","elementType":"geometry.fill","stylers":[{"color":"#f4f4f4"}]},{"featureType":"road.arterial","elementType":"labels.text.fill","stylers":[{"color":"#787878"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#eaf6f8"},{"visibility":"on"}]},{"featureType":"water","elementType":"geometry.fill","stylers":[{"color":"#eaf6f8"}]}]
						styles: [{"featureType":"landscape","stylers":[{"hue":"#FFBB00"},{"saturation":43.400000000000006},{"lightness":37.599999999999994},{"gamma":1}]},{"featureType":"road.highway","stylers":[{"hue":"#FFC200"},{"saturation":-61.8},{"lightness":45.599999999999994},{"gamma":1}]},{"featureType":"road.arterial","stylers":[{"hue":"#FF0300"},{"saturation":-100},{"lightness":51.19999999999999},{"gamma":1}]},{"featureType":"road.local","stylers":[{"hue":"#FF0300"},{"saturation":-100},{"lightness":52},{"gamma":1}]},{"featureType":"water","stylers":[{"hue":"#0078FF"},{"saturation":-13.200000000000003},{"lightness":2.4000000000000057},{"gamma":1}]},{"featureType":"poi","stylers":[{"hue":"#00FF6A"},{"saturation":-1.0989010989011234},{"lightness":11.200000000000017},{"gamma":1}]}]
						// styles: [{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#444444"}]},{"featureType":"administrative.country","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"administrative.country","elementType":"geometry","stylers":[{"visibility":"off"}]},{"featureType":"administrative.country","elementType":"geometry.fill","stylers":[{"visibility":"off"}]},{"featureType":"administrative.country","elementType":"geometry.stroke","stylers":[{"visibility":"off"}]},{"featureType":"administrative.province","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"administrative.locality","elementType":"labels","stylers":[{"hue":"#ffe500"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"},{"visibility":"on"}]},{"featureType":"landscape.natural","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"landscape.natural.landcover","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"landscape.natural.terrain","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"landscape.natural.terrain","elementType":"geometry","stylers":[{"visibility":"on"}]},{"featureType":"landscape.natural.terrain","elementType":"geometry.fill","stylers":[{"visibility":"on"}]},{"featureType":"landscape.natural.terrain","elementType":"geometry.stroke","stylers":[{"visibility":"on"}]},{"featureType":"landscape.natural.terrain","elementType":"labels","stylers":[{"visibility":"on"}]},{"featureType":"landscape.natural.terrain","elementType":"labels.text","stylers":[{"visibility":"on"}]},{"featureType":"landscape.natural.terrain","elementType":"labels.text.fill","stylers":[{"visibility":"on"}]},{"featureType":"landscape.natural.terrain","elementType":"labels.text.stroke","stylers":[{"visibility":"on"}]},{"featureType":"landscape.natural.terrain","elementType":"labels.icon","stylers":[{"visibility":"on"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"poi.attraction","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"poi.business","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"poi.place_of_worship","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"poi.school","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45},{"visibility":"on"}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"transit.station","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"transit.station.airport","elementType":"all","stylers":[{"visibility":"on"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#9bdffb"},{"visibility":"on"}]}]
					};

				var map= new google.maps.Map(mapCanvas, mapOptions);
				// var marker= new google.maps.Marker({position: new google.maps.LatLng(self.lat, self.long), map: map});

				self.map= map;

				// var circleSettings = {strokeColor: '#4EB1BA', strokeOpacity: 0.8, strokeWeight: 2, fillColor: '#4EB1BA', fillOpacity: 0.35,
				// 	map: map, center:  new google.maps.LatLng(self.lat, self.long), radius: 1000 };

				// var circle = new google.maps.Circle(circleSettings);
				// map.fitBounds(circle.getBounds());

				// var trafficLayer = new google.maps.TrafficLayer();
				// trafficLayer.setMap(map);

				self.infoWindow= new google.maps.InfoWindow({content: ""});

				self.showMarkers();

				// $('.google-map_card').pushpin({ top: $('.google-map_card #googleMap').offset().top });
			});
		}
	});
});