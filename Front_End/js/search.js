$(document).ready(function(){
window.make_request = function make_request(data, algorithm){ url =  window.process_text_url ; return $.post(url, {"text": data, "algorithm": algorithm}) }
App.RootView = Backbone.View.extend({
	//tagName: "fieldset",
	//className: "well-lg plan",
	
	initialize: function(){
		var self = this;
			},
	
	render: function(){
		var subView = new App.MainView();
		$(".dynamic-display").append(subView.render().el);	
		return this;
	},

});


App.MainView = Backbone.View.extend({
	tagName: "form",
	className: "form-horizontal",
	template: window.template("root"),
	initialize: function(){
		var self = this;
		/*
		
		$(".side-bar").html(this.render().el);
			*/
		},

	render: function(){
		var self = this;
		this.beforeRender();	

		this.$el.css("margin-left: 1px; margin-right: px")
		this.$el.append(this.template(this));
		
		var jqhr = $.get(window.limited_eateries_list)	
		jqhr.done(function(data){
			if (data.error == false){
				$.each(data.result, function(iter, eatery){
					var subView = new App.AppendEateries({"model": eatery});
					__html = subView.render().el
					self.$(".eateries-list").append(__html);	
				
				})
				/*
				$.each(data.result, function(iter, eatery){
					var subView = new App.AppendRestaurants({"eatery": eatery});
					self.$(".append_eatery").append(subView.render().el);	
				*/
				self.$(".eateries-list li").on('click', function(){
						self.$(".eatery-list-button:first-child").text($(this).text());
			       			self.$(".eatery-list-button:first-child").val($(this).text());
			       			self.$(".eatery-list-button:first-child").attr("eatery_id", $(this).attr("eatery_id"));
			       			self.$(".eatery-list-button:first-child").attr("lat", $(this).attr("lat"));
			       			self.$(".eatery-list-button:first-child").attr("long", $(this).attr("long"));
						       
				});
					}



			else{
			}
		})
		this.$(".range li").on('click', function(){
			      $(".range-button:first-child").text($(this).text());
			            $(".range-button:first-child").val($(this).val());
				       });
			
		return this;
	},

	beforeRender: function(){
		var subview = new App.TrendingView();
		subview.render().el;
		__array = [{'eatery_name': 'Cheese Chaplin', 'eatery_coordinates': [28.5244611111, 77.1919944444]}, 
			{'eatery_name': 'Chef &amp; I', 'eatery_coordinates': [28.5246305556, 77.1914527778]}, 
			{'eatery_name': 'Cafe Seclude', 'eatery_coordinates': [28.5245277778, 77.1909777778]}, 
			{'eatery_name': 'Shroom', 'eatery_coordinates': [28.524948, 77.190225]}, 
			{'eatry_name': 'Lure Switch', 'eatery_coordinates': [28.5291066667, 77.1936133333]}]			
		__initial_lat = 28.6427138889;
		__initial_long = 77.1192555556;
		this.reloadGoogleMap(__initial_lat, __initial_long, __array);
	},
	
	events: {
		'click .submitButton': 'Submit', 	
		'click .change-map': 'changeMap',
		},

	changeMap: function(event){
		event.preventDefault();
		var self = this;
		eatery_lat = $(".eatery-list-button").attr("lat")
		eatery_long = 	$(".eatery-list-button").attr("long")
		range = $(".range-button").val()
		
		var jqhr = $.post(window.nearest_eateries, {"lat": eatery_lat, "long": eatery_long, "range": range})	
		jqhr.done(function(data){
			if (data.error == false){
				
				self.reloadGoogleMap(eatery_lat, eatery_long, data.result)
					}
			else{
				var subView = new App.ErrorView();
				$(".trending-bar-chart").html(subView.render().el);	
			}
		})
		
		jqhr.fail(function(data){
				var subView = new App.ErrorView();
				$(".dynamic-display").html(subView.render().el);	
						
		});
		
		},


	reloadGoogleMap: function (__initial_lat, __initial_long, eateries_list){
		function initialize() {
			var mapCanvas = document.getElementById('map-canvas');
			var mapOptions = {
					center: new google.maps.LatLng(__initial_lat, __initial_long),
					zoom: 19,
					mapTypeId: google.maps.MapTypeId.ROADMAP
                                          }
			var map = new google.maps.Map(mapCanvas, mapOptions)
			map.set('styles', [
					{
						featureType: 'poi',
						elementType: 'geometry',
						stylers: [
							{hue: '#fff700' },
							{lightness: -15 },
							{saturation: 99 }
							]
					}]);
			$.each(eateries_list, function(iter, data){
                                marker = new google.maps.Marker({
                                map: map,
                                position: new google.maps.LatLng(data.eatery_coordinates[0], data.eatery_coordinates[1]),
                                title: data.eatery_name,
				eatery_id: data.eatery_id, 
				address: data.eatery_address,
				html: "<div id='infobox'>" + data.eatery_name + "</br>" + data.eatery_address + "</div>" 

                                })
                                google.maps.event.addListener(marker, 'mouseover', function() {
					infowindow.setContent(this.html);        
					infowindow.open(map, this);        
					});
                                
				google.maps.event.addListener(marker, 'mouseout', function() {
					infowindow.close();        
					});
				google.maps.event.addListener(marker, 'click', function() {
					console.log(marker.get("eatery_id"));        
					});
                        })
                       
		       			
				var infowindow = new google.maps.InfoWindow({
					      content: "",
					  });

		}
			initialize();
		},




	Submit: function(event){
		event.preventDefault();
		console.log("Button pressed");
		value = $("#searchQuery").val();
			
		if (value == ""){
				console.log("No result");
			}
		console.log(value)
		var jqhr = $.post(window.resolve_query, {"text": value})	
		jqhr.done(function(data){
			if (data.error == false){
				console.log(data.result)
				var subView = new App.ResultView({"model": data.result, "text": value});
				$("body").html(subView.render().el);	
								
				/*
				$.each(data.result, function(iter, eatery){
					var subView = new App.AppendRestaurants({"eatery": eatery});
					self.$(".append_eatery").append(subView.render().el);	
				*/
					}
			else{
				var subView = new App.ErrorView();
				$(".trending-bar-chart").html(subView.render().el);	
			}
		})
		
		jqhr.fail(function(data){
				var subView = new App.ErrorView();
				$(".dynamic-display").html(subView.render().el);	
						
		});
		}, 
			


	seeWordCloud: function(eatery_id){
		$(".main-body").empty()
		
			
		var subView = new App.SeeWordCloudDateSelectionView();
		bootbox.dialog({
			"title": "Word Cloud: " + $(":checkbox:checked").val() ,
			"message": subView.render().el,
			"animate": true,
			"closeButton": true,
			"className": "data_selection",
			})
	},
	});


App.AppendEateries = Backbone.View.extend({
	tagName: "li",
	name: function(){return this.model.eatery_name},
	template: window.template("append-eatery"),
	initialize: function(options){
		this.model = options.model;
		var self = this;
		},

	render: function(){
		this.$el.attr("lat", this.model.eatery_coordinates[0]);
		this.$el.attr("long", this.model.eatery_coordinates[1]);
		this.$el.attr("eatery_id", this.model.eatery_id);
		this.$el.attr("value", this.model.eatery_name);
		this.$el.append(this.template(this));
		return this;
	},

	})
App.ErrorView = Backbone.View.extend({
	tagName: "div",
	template: window.template("error"),
	initialize: function(){
		var self = this;
		/*
		
		$(".side-bar").html(this.render().el);
			*/
		},

	render: function(){
		this.$el.append(this.template(this));
		return this;
	},

	})

});



