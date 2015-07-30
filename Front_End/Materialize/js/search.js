$(document).ready(function(){
$('.scrollspy').scrollSpy();
       

$('.modal-trigger3').leanModal({
	dismissible: true, // Modal can be dismissed by clicking outside of the modal
	opacity: .5, // Opacity of modal background
	in_duration: 300, // Transition in duration
	out_duration: 200, // Transition out duration
	complete: function() { 
			var result = {"name": $("#feedback input")[0].value, 
					"telephone": $("#feedback input")[1].value,
					"email": $("#feedback input")[2].value,
					"feedback": $("#feedback textarea").val()
			
			}
	} // Callback for Modal close
		    }
		      );
$('.modal-trigger').leanModal({
	dismissible: true, // Modal can be dismissed by clicking outside of the modal
	opacity: .5, // Opacity of modal background
	in_duration: 300, // Transition in duration
	out_duration: 200, // Transition out duration
	complete: function() { 
			var result = {"name": $("#feedback input")[0].value, 
					"telephone": $("#feedback input")[1].value,
					"email": $("#feedback input")[2].value,
					"feedback": $("#feedback textarea").val()
			
			}
			console.log(result);
			Materialize.toast('Thank you for your feedback', 2000)
	} // Callback for Modal close
		    }
		      );
$('.modal-trigger2').leanModal({
	dismissible: true, // Modal can be dismissed by clicking outside of the modal
	opacity: .5, // Opacity of modal background
	in_duration: 300, // Transition in duration
	out_duration: 200, // Transition out duration
	complete: function() { 
					query  = $("#searchQuery textarea").val()
					console.log(query)
			if (query == ""){
				Materialize.toast('Please write something to let us, help you finding the awesomeness', 2000)
				}
			else{
				Materialize.toast('Please wait while we process your Query', 2000)
			
			}
			}}
		      );



window.make_request = function make_request(data, algorithm){ url =  window.process_text_url ; return $.post(url, {"text": data, "algorithm": algorithm}) }
var jqhr = $.get(window.limited_eateries_list)	
jqhr.done(function(data){
			if (data.error == false){
				$.each(data.result, function(iter, eatery){
					var subView = new App.AppendEateries({"model": eatery});
					__html = subView.render().el
					$(".eateries-list").append(__html);	
				
				})
				/*
				$.each(data.result, function(iter, eatery){
					var subView = new App.AppendRestaurants({"eatery": eatery});
					self.$(".append_eatery").append(subView.render().el);	
				*/

				$("#change-map li").on("click", function(){
						eatery_lat = $(this).attr("lat")
						eatery_long = 	$(this).attr("long")
						range = 10;
		
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
							});
							}


		
						else{
						}
					})
$('.dropdown-button').dropdown({
	      inDuration: 300,
	      outDuration: 225,
	      constrain_width: false, // Does not change width of dropdown to that of the activator
	      hover: true, // Activate on hover
	      gutter: 0, // Spacing from edge
	      belowOrigin: false // Displays dropdown below the button
	    }
	      );
	
		


reloadGoogleMap =  function (__initial_lat, __initial_long, eateries_list){
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
					console.log(this.get("eatery_id"));     
				     	var subView = new App.EateryDetails({"model": {"eatery_id": this.get("eatery_id"), "eatery_name": this.get("title")}});	
					subView.render().el;
					});
                        })
                       
		       			
				var infowindow = new google.maps.InfoWindow({
					      content: "",
					  });

		}
			initialize();

		};

App.RootView = Backbone.View.extend({
	//tagName: "fieldset",
	//className: "well-lg plan",
	
	initialize: function(){
		var self = this;
			},
	
	events: {
		'click .feedbackForm': 'feedbackForm', 	
		},



	feedbackForm: function(event){
		event.preventDefault();
		console.log("feedback form clicked");
		},
	render: function(){
		var subView = new App.MainView();
		$(".dynamic-display").append(subView.render().el);	
		this.$('.collapsible').collapsible({
			      accordion : false // A setting that changes the collapsible behavior to expandable instead of the default accordion style
			    });
		return this;
	},

});


App.MainView = Backbone.View.extend({
	className: "row",
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
		this.$el.append(this.template(this));
		this.$el.attr("style",  "margin-bottom: 0px");
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
		'click .feedbackForm': 'feedbackForm', 	
		},



	feedbackForm: function(event){
		event.preventDefault();
		console.log("feedback form clicked");
		},

	changeMap: function(event){
		event.preventDefault();
		var self = this;
		eatery_lat = $(".eatery-list-button").attr("lat")
		eatery_long = 	$(".eatery-list-button").attr("long")
		range = 10;
		
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
					console.log(this.get("eatery_id"));     
				     	var subView = new App.EateryDetails({"model": {"eatery_id": this.get("eatery_id"), "eatery_name": this.get("title")}});	
					subView.render().el;
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
		value = $("textarea").val();
			
		if (value == ""){
				console.log("No result");
			}
		console.log(value)
		var jqhr = $.post(window.resolve_query, {"text": value})	
		jqhr.done(function(data){
			if (data.error == false){
				/*{'ambience': ['decor'], 'food': {}, 'cost': [], 'service': [], 
				 * 'sentences': {'food': [(u'i want to have awesome chicken tikka t', u'dishes')], 
				 * 'ambience': [(u'would have nice decor .', u'decor')], 'cost': [], 'service': []}}
				 */
				$(".show-sentences").html("");
				console.log(data.result)
				var subView = new App.DisplaySuggestion({"model": data.result})
				$(".show-sentences").append(subView.render().el);

				/*
				$.each(["food", "service", "cost", "ambience"], function(iter, tag){
						
						var subView = new App.DisplaySuggestion({"model": {"name": tag, "data": data["result"][tag]}})
						$(".show-sentences").append(subView.render().el);
				})
				$.each(["food", "service", "cost", "ambience", "overall"], function(iter, tag){
						$.each(data["result"]["sentences"][tag], function(__iter, __data){
						
						var subView = new App.DisplaySuggestion({"model": {"name": tag + " sentences", "data": __data}})
						$(".show-sentences").append(subView.render().el);
						})	
				})
				
				*/				
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


App.DisplaySuggestion = Backbone.View.extend({
	tagName: "ul", 
	className: "collapsible",
	template: window.template("display"),
	name : function(){return this.model.name},
	suggestions : function(){ if (this.model.name == "food"){
					return this.model.data["dishes"]}
				else{
					return this.model.data}},
	intialize: function(options){
		this.model = options.model;

	},

	render: function(){
		this.$el.append(this.template(this));
		this.$el.attr("data-collapsible", "accordion");
		return this;

	},

});


App.EateryDetails = Backbone.View.extend({
	initialize: function(options){
		this.model = options.model;
		
		console.log("Called from Eatery details");
		console.log(this.model.eatery_id);
		console.log(this.model.eatery_name);
		},

	render: function(){
		var self = this;
		var jqhr = $.post(window.eatery_details, {"eatery_id": this.model.eatery_id})	
		jqhr.done(function(data){
			if (data.error == false){
				console.log(data.result)
				$.each(["food", "ambience", "cost", "service"], function(iter, value){
					__object = $("#" + value);	
					self.makeChart(__object, data.result[value], self.model.eatery_name, value);
				})
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
		return this;
	},

	makeChart: function(__object,  __data, eatery_name, category){
			__object.highcharts({

				chart: {
						        renderTo: 'container',
				        type: 'bar',
				        alignTicks: false,
				        plotBackgroundColor: null,
				        plotBackgroundImage: null,
				        plotBorderWidth: 2,
				        plotShadow: false,
					    },
				
				credits: {
					enabled: false
				                        },
        			title: {
            				//text: category + " word cloud, " + eatery_name
            				text: ""
        				},
        			xAxis: {
            				categories: __data.categories,
        				},
        			yAxis: {
            				min: 0,
            				title: {
                				text: 'total frequency'
            					}, 
					lineColor: '#339',
							        tickColor: '#339',
									        minorTickColor: '#339',
        				},
        			legend: {
            				reversed: true
        				},
        			plotOptions: {
					   groupPadding:0.1,
					                     pointWidth:20,
							                       pointPadding: 0,
            				
					
					series: {
						animation: {
							                    duration: 2000,
									                        easing: 'easeOutBounce'
													                },
                				stacking: 'normal'
            					}
        					},
        			series: __data.series, 
				exporting: { enabled: false }	
    						});
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

	});

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



