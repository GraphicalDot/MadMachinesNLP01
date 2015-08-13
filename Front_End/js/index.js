$(document).ready(function(){
$.fn.enterKey = function (fnc) {
		return this.each(function () {
			$(this).keypress(function (ev) {
				var keycode = (ev.keyCode ? ev.keyCode : ev.which);
				if (keycode == '13') {
					fnc.call(this, ev);
						}
					})
			})
}




App.PickEatery = Backbone.View.extend({
	//tagName: "fieldset",
	//className: "well-lg plan",
	
	initialize: function(options){
		this.model = options.model
			},
	
	render: function(){
		var table = '<table id="pickEatery">'+
				'<thead>'+
					'<tr style="color: #4EB1BA; font-weight: bold">'+
						'<th data-field="id">eatery name</th>'+
						'<th data-field="trending1">Trending 1</th>'+
						'<th data-field="trending2">Trending 2</th>'+
						'<th data-field="cost">cost</th>'+
						'<th data-field="service">service</th>'+
						'<th data-field="ambience">ambience</th>'+
					'</tr>'+
				'</thead>'+
      				'<tbody id="table-body">'+
				'<tbody>'+
			'</table>'	
		this.$el.append(table)
		this.beforerender();
		return this;
	},
	
	beforerender: function(){
		var self = this;
		var jqhr = $.post(window.eateries_on_character, {"page_num": self.model.page_num})	
		jqhr.done(function(data){
			if (data.error == false){
				$.each(data.result, function(iter, eatery){
					var subView = new App.PickEateryChild({"model": eatery});
					self.$("#table-body").append(subView.render().el)
				
				})
			}

		//Deals with the sorting of the pick eatery table
		self.$("#pickEatery").tablesorter();
		})
		return 
	},
	
});


App.PickEateryChild = Backbone.View.extend({
	tagName: "tr",
	template: window.template("pick-eatery-child"),
	eatery_name: function(){ return this.model.eatery_name},
	trending1: function(){ return this.model.trending1},
	trending2: function(){ return this.model.trending2},
	cost: function(){ return this.model.cost},
	service: function(){ return this.model.service},
	ambience: function(){ return this.model.ambience},

	initialize: function(options){
		this.model = options.model;
			},
	
	render: function(){
		this.$el.append(this.template(this));
		this.$el.attr("lat", this.model.eatery_coordinates[0]);
		this.$el.attr("long", this.model.eatery_coordinates[1]);
		this.$el.attr("eatery_id", this.model.eatery_id);
		this.$el.attr("style", "color: #E9E9E9");
		return this;

	},

	events: {
		"click .eatery-row":  "clicked"
	},

	clicked: function(event){
		var self = this;
		event.preventDefault();
		console.log("clicked" + this.model.eatery_id)
		$("#food").html(window.loaderstring)
		eatery_lat = this.model.eatery_coordinates[0]
		eatery_lng = this.model.eatery_coordinates[1]
		var subView = new App.ModifyViewOnEatery({"model": {"eatery_id": this.model.eatery_id, "eatery_name": this.model.eatery_name, "eatery_lat": eatery_lat, "eatery_lng": eatery_lng}});	
		subView.render().el
	},
})



App.ModifyViewOnEatery = Backbone.View.extend({

	initialize: function(options){
			//eatery_id, eatery_name, eatery_lat, eatery_lng)
			this.model = options.model;
			console.log(this.model)
		},
		/*this is a function which will change tranding view and eatery details view when a eatery is clicked either from the
		 * pick eatery menu or search eatery bar
		 */
	
	
	render: function(){
		var self = this;
		var subView = new App.EateryDetails({"model": {"eatery_id": this.model.eatery_id, "eatery_name": this.model.eatery_name}});	
		subView.render().el;
		
		range = 10;
		
		var jqhr = $.post(window.nearest_eateries, {"lat": this.model.eatery_lat, "long": this.model.eatery_lng, "range": range})	
		jqhr.done(function(data){
			if (data.error == false){
			
				console.log(data.result)	
				reloadGoogleMap(self.model.eatery_lat, self.model.eatery_lng, data.result)
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

			//http://suprb.com/apps/gridalicious/			
		//Updating trending view 	
		var jqhr = $.post(window.get_trending, {"lat": this.model.eatery_lat, "lng": this.model.eatery_lng,})	
		jqhr.done(function(data){
			if (data.error == false){
				$(".grid-grid").html("");
				
				
				$(".grid-grid").append('<div class="grid-item-new  card #222930 blue-grey darken-4 z-depth-3" style="text-align: center"> <p>Trending </p><p>near</p><p>' + self.model.eatery_name + '</p>')
				var subView = new App.WriteReview({"model": {"eatery_id": self.model.eatery_id, "eatery_name": self.model.eatery_name}});
				$(".grid-grid").append(subView.render().el);	
				//$(".grid-grid").append('<div class="grid-item-new  card #222930 blue-grey darken-4 z-depth-3" style="text-align: center"> <p>Write review for<p>' + self.model.eatery_name + '</p>')

				$.each(["food", "service", "cost", "ambience"], function(iter, category){
						$.each(data.result[category], function(iter2, model){
							model["category"] = category   
							var subview = new App.DataView({"model": model})
							//list.push(subview.render().el);	
							$(".grid-grid").append(subview.render().el);
							
						   })
						 });   		 
				$(".grid-grid").gridalicious({selector: '.grid-item-new',
						gutter: 1, 
						width: 200,
						animate: true,
					  animationOptions: {
						      queue: true,
					    speed: 200,
					    duration: 300,
					    effect: 'fadeInOnAppear',
					  }
				
				})}
				else{
					var subView = new App.ErrorView();
					$(".trending-bar-chart").html(subView.render().el);	
				}
			})
			return this;
			}, 


		});






App.WriteReview = Backbone.View.extend({
	className: "grid-item-new  card #222930 blue-grey darken-4 z-depth-3",
	template: window.template("write-review"),
	eatery_name : function(){ return this.model.eatery_name},
	eatery_id: function(){ return this.model.eatery_id},
	initialize: function(options){
			this.model = options.model;
	},

	render: function(){
		this.$el.append(this.template(this));
		this.$el.attr("eatery_id", this.model.eatery_id);
		this.$el.attr("style", "text-align: center");
		return this;
	},

	events: {
		"click .write-review": "writeReviewfunction", 
	},

	writeReviewfunction: function(event){
		var self = this;
		event.preventDefault();
		console.log("Write review has been clicked with" + this.model.eatery_id);
		var subView = new App.WriteReviewChild({"model": {"eatery_id": this.model.eatery_id, "eatery_name": this.model.eatery_name}})
		$("body").append(subView.render().el);
		$('.modal-trigger').leanModal({
			       dismissible: true, // Modal can be dismissed by clicking outside of the modal
			       opacity: .5, // Opacity of modal background
			       ready: function() {
				      	console.log($("modal32").attr("eatery_id")) 
					$("#modal32 label").text("write review for" + self.model.eatery_name);
			       		alert('Ready');		
			       
			       
			       }, // Callback for Modal open
			       complete: function() { 
				       
			       } // Callback for Modal close
		     }
		       );
		$("#modal32").openModal();
	},
});


App.WriteReviewChild = Backbone.View.extend({
	className: "modal-trigger modal #222930 blue-grey darken-4",
	template: window.template("write-review-child"),
	eatery_name: function(){ return this.model.eatery_name},


	initialize: function(options){
		this.model = options.model;  
	},

	render: function(){
		this.$el.append(this.template(this));
		this.$el.attr("id", "modal32");
		this.$el.attr("eatery_id", this.model.eatery_id);
		return this;
	},


	events: {
	},

	submitReview: function(event){
		var self = this;
		event.preventDefault();
		$("#modal32").closeModal();
			
	},



});

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
		       		google.maps.event.addListener(map, 'click', function(event) {
					    marker = new google.maps.Marker({position: event.latLng, map: map});
				});

		}
			initialize();

		};

App.BodyView = Backbone.View.extend({
	//tagName: "fieldset",
	//className: "well-lg plan",
	
	initialize: function(){
		var self = this;
		$('.modal-trigger3').leanModal({
				//This is for how it works options, Whihch hasnt been implemented yet
				dismissible: true, // Modal can be dismissed by clicking outside of the modal
				opacity: .5, // Opacity of modal background
				in_duration: 300, // Transition in duration
				out_duration: 200, // Transition out duration
				complete: function() { }, });
		
		$("#pickEatery").on("click", function(){
			console.log("pick eatery clicked");
			self.clickPickEatery()
				});
		
		$(".button-collapse").sideNav();
	},



	
	render: function(){
		var self = this;
			if (navigator.geolocation){
				navigator.geolocation.getCurrentPosition(showPosition);
			} 
			else{
				console.log("Location coundnt be rendered")	
			}
		function showPosition(position) {
			console.log("Latitude: " + position.coords.latitude + "Longitude: " + position.coords.longitude) 
			var latitude = position.coords.latitude;
			var longitude = position.coords.longitude


			//On the basis of the current location gets the trending dishes, mbienece, service and cost clouds
			var jqhr = $.post(window.nearest_eateries, {"lat": latitude, "long": longitude, "range": 10})	
			jqhr.done(function(data){
				console.log(data.result);
				if (data.error == false){
					self.reloadGoogleMap(latitude, longitude, data.result)
					}
				else{
					var subView = new App.ErrorView();
					$(".trending-bar-chart").html(subView.render().el);	
				}
			
			})
			var jqhr = $.post(window.get_trending, {"lat": latitude, "lng": longitude,})	
			jqhr.done(function(data){
				console.log(data.result);
				if (data.error == false){
					$.each(["food", "service", "cost", "ambience"], function(iter, category){
						$.each(data.result[category], function(iter2, model){
							console.log(model)
							model["category"] = category   
							var subview = new App.DataView({"model": model})
							$(".grid-grid").append(subview.render().el);
						   }) 
						 });   		 
				
				
				}
				else{
					var subView = new App.ErrorView();
					$(".trending-bar-chart").html(subView.render().el);	
				}
			
				$(".grid-grid").gridalicious({selector: '.grid-item-new',
						gutter: 1, 
						width: 150,
						animate: true,
					  animationOptions: {
						      queue: true,
					    speed: 200,
					    duration: 300,
					    effect: 'fadeInOnAppear',
					  }
				
				})
			
			})
			
		};


			//Deals with if somebody wants to enetr a query out of which we have to figure out what he wants and a which eatery he wants
			this.intiateEnterQuery();	

			//Deals with if somebdy wants to provide feedback
			this.intiateFeedback();

			//Deals with the two search bars which will have enter dish name and enter eatery name
			this.initiateAutoComplete();



		return this;
	},
		//Appends eateries to the etery selection id of the body, PickEateryChild is the view which binds a click event 
		//on the every eatery present in the bootpeg table, When clicks it should render all the details of the eatery and then fetches the details of the eatery 
		
	events: {
	
	},

	initiateAutoComplete: function(){
			//deals with the autocomplete by rendering data from elastic search and using typeahead.js library
			//binds two events, one is  selection from typehead and enter key from typehead and the event is 
			//to call dishSuggestions method of this view with the dish name
			//and on eatery selection calls the eatery details view in this file which will generate the 
			//fur clouds for the particular eatery
			var self = this;
			$('.search-dish').typeahead({
					  hint: true,
					  highlight: true,
					  minLength: 4,
				},
				{
					limit: 12,
					async: true,
					select: function(event, name) {
							console.log(name)		            
					},
					source: function (query, processSync, processAsync) {
						          return $.ajax({
								        url: window.get_dish_suggestions, 
								       type: 'GET',
								       data: {query: query},
								       dataType: 'json',
								       success: function (json) {
										       return processAsync(json.options);
										     }
									});
							}
			});

			$(".search-dish").enterKey(function () {
				var dish_name = $(this).val();
				self.dishSuggestions(dish_name)
			})
		
			$('.search-dish').bind('typeahead:select', function(ev, suggestion) {
				  alert('Selection: ' + suggestion);
			});

			
			$('.search-eatery').typeahead({
					  hint: true,
					  highlight: true,
					  minLength: 2,
				},
				{
					  limit: 12,
					  async: true,
					  source: function (query, processSync, processAsync) {
						          return $.ajax({
								        url: window.get_eatery_suggestions, 
								       type: 'GET',
								       data: {query: query},
								       dataType: 'json',
								       success: function (json) {
										       return processAsync(json.options);
										     }
									});
							}
			});
			
			$(".search-eatery").enterKey(function () {
				alert('Enter pressed n search-eatery');
			})
	},


	dishSuggestions: function(dish_name){
		//Fetches relevant matched from elastic search ont he basis of the dish_name given to it
		var jqhr = $.post(window.get_dishes, {"dish_name": dish_name})	
		jqhr.done(function(data){
			if (data.error == false){
				$(".grid-dish-suggestions").html("");
				
				
				$(".grid-dish-suggestions").append('<div class="grid-item-dish-suggestions  card #222930 blue-grey darken-4 z-depth-3" style="text-align: center"> <p>Match </p><p>for</p><p>' + dish_name + '</p>')

				$.each(data.result, function(iter, model){
							var subview = new App.DataDishSuggestionsView({"model": model})
							//list.push(subview.render().el);	
							$(".grid-dish-suggestions").append(subview.render().el);
							
						   })
				$(".grid-dish-suggestions").gridalicious({selector: '.grid-item-dish-suggestions',
						gutter: 1, 
						width: 200,
						animate: true,
					  animationOptions: {
						      queue: true,
					    speed: 200,
					    duration: 300,
					    effect: 'fadeInOnAppear',
					  }
				
				})
				}
				else{
					var subView = new App.ErrorView();
					$(".trending-bar-chart").html(subView.render().el);	
				}
		
			})
	},




	intiateFeedback: function(){
		$('.modal-trigger').leanModal({
			//This is for the feedback form 
			dismissible: true, // Modal can be dismissed by clicking outside of the modal
			opacity: .5, // Opacity of modal background
			in_duration: 300, // Transition in duration
			out_duration: 200, // Transition out duration
			complete: function() { 
				if ($("#feedback textarea").val()){
						Materialize.toast('Thank you for your feedback', 2000)
						$.post(window.users_feedback, {"feedback": $("#feedback textarea").val(), 
								"telephone": $("#feedback input")[1].value,
								"email": $("#feedback input")[2].value,
								"name": $("#feedback input")[0].value, 
								})
			
				}
					} // Callback for Modal close
		    		});


	},

	clickPickEatery: function(){
		//Generates a table with bootpeg.js for the eateries right now sorted on the basis of the data present in the database.
		//alo implements the pagination for the eateries by calling in PickEatery view in the file
		console.log("click eatery has been clicked");	
		var subview = new App.PickEatery({"model": {"page_num": 0}})
		$("#eatery-content").html(subview.render().el); // or some ajax content loading...

		$('#eatery-page-selection').bootpag({
				total: 700,
				page: 1,
				maxVisible: 10,
				leaps: true,
				firstLastUse: true,
				first: '←',
				last: '→',
				wrapClass: 'pagination',
				activeClass: 'active',
				disabledClass: 'disabled',
				nextClass: 'next',
				prevClass: 'prev',
				lastClass: 'last',
				firstClass: 'first'}).on('page', function(event, num){
							console.log('<p>Let it be loaded</p>')
							subview = new App.PickEatery({"model": {"page_num": num}})
							$("#eatery-content").html(window.loaderstring);
							$("#eatery-content").html(subview.render().el);
					});
			
		 var container = $(".pickEateryRow");
			
	},

	reloadGoogleMap: function (__initial_lat, __initial_long, eateries_list){
		function initialize() {
			var mapCanvas = document.getElementById('map-canvas');
			var mapOptions = {
					center: new google.maps.LatLng(__initial_lat, __initial_long),
					zoom: 19,
					mapTypeId: google.maps.MapTypeId.ROADMAP,
                                        styles: [{"featureType": "all",
							"elementType": "all",
							"stylers": [
								{"invert_lightness": true},
								{"saturation": 10},
								{"lightness": 30},
								{"gamma": 0.5},
								{"hue": "#435158"},]
						}],
					draggable: true,
					
			};
			var map = new google.maps.Map(mapCanvas, mapOptions)
			console.log("From the function reload google map");
					    marker = new google.maps.Marker({position: new google.maps.LatLng(__initial_lat, __initial_long), 
						    map: map, 
					    		icon: 'css/location-icon.png',});
				
					var circleSettings = {
						      strokeColor: '#4EB1BA',
				      strokeOpacity: 0.8,
				      strokeWeight: 2,
				      fillColor: '#4EB1BA',
				      fillOpacity: 0.35,
				      map: map,
				      center:  new google.maps.LatLng(__initial_lat, __initial_long),
				      radius: 1000
					    };
					circle = new google.maps.Circle(circleSettings);
					map.fitBounds(circle.getBounds());	
			var trafficLayer = new google.maps.TrafficLayer();
			  trafficLayer.setMap(map);
			console.log(eateries_list)
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
					infowindow.setContent(this.get("html"));        
					infowindow.open(map, this);       
				       console.log(this.html)
					console.log(this.get("html"))	
					});
                                
				google.maps.event.addListener(marker, 'mouseout', function() {
					infowindow.close();        
					});
				google.maps.event.addListener(marker, 'click', function() {
					console.log(this.get("eatery_id"));     
				     	var subView = new App.EateryDetails({"model": {"eatery_id": this.get("eatery_id"), "eatery_name": this.get("title")}});	
					subView.render().el;
					//subView.render().el;
					});
                        })
                       
		       		google.maps.event.addListener(map, 'click', function(event) {
				
				});

		}
			initialize();
		},


		intiateEnterQuery:  function (){ 
			$('.modal-trigger2').leanModal({
				//This is for taking in user query for the search
				dismissible: true, // Modal can be dismissed by clicking outside of the modal
				opacity: .5, // Opacity of modal background
				in_duration: 300, // Transition in duration
				out_duration: 200, // Transition out duration
				complete: function() { 
					value  = $("#searchQuery textarea").val()
					console.log(value)
					if (value == ""){
						Materialize.toast('Please write something to let us, help you finding the awesomeness', 2000)
					}
				else{
						Materialize.toast('Please wait while we process your Query', 2000)
					var jqhr = $.post(window.resolve_query, {"text": value})	
					jqhr.done(function(data){
					if (data.error == false){
						$(".queryResult").html("");
						console.log(data.result)
						var subView = new App.DisplaySuggestion({"model": data.result})
						$(".queryResult").append(subView.render().el);
					}
		})
		
		jqhr.fail(function(data){
						
		});
			}
			}}
		      );
		},
});


App.DataDishSuggestionsView = Backbone.View.extend({
	className: "grid-item-dish-suggestions  card #222930 z-depth-3",
	template: window.template("data-dish-suggestions"),
	name : function(){ return this.model.name},
	positive : function(){ return this.model.positive},
	negative : function(){ return this.model.negative},
	neutral : function(){ return this.model.neutral},
	supernegative : function(){ return this.model.supernegative},
	superpositive : function(){ return this.model.superpositive},
	eatery_name : function(){ return this.model.eatery_name},
	initialize: function(options){
		var self = this;
		this.model = options.model;
		},

	render: function(){
		var self = this;
		this.$el.append(this.template(this));
		this.$el.attr("color", "white");

		return this;
	},

	events: {
		"click .data-click-eatery": "ClickEatery",
	
	},

	ClickEatery: function(event){
		var self = this;
		event.preventDefault();
		console.log("Eatery has been clicked");
		console.log(self.model.eatery_id);
		var subView = new App.ModifyViewOnEatery({"model": {"eatery_id": self.model.eatery_id, "eatery_name": self.model.eatery_name, "eatery_lat": self.model.location.lat, "eatery_lng": self.model.location.lon}});	
		subView.render().el

	},

});
	
	
App.DataView = Backbone.View.extend({
	className: "grid-item-new  card #222930 z-depth-3",
	template: window.template("data"),
	category : function(){ return this.model.category},
	name : function(){ return this.model.name},
	positive : function(){ return this.model.positive},
	negative : function(){ return this.model.negative},
	neutral : function(){ return this.model.neutral},
	supernegative : function(){ return this.model.supernegative},
	superpositive : function(){ return this.model.superpositive},
	eatery_name : function(){ return this.model.eatery_name},
	initialize: function(options){
		var self = this;
		this.model = options.model;
		},

	render: function(){
		var self = this;
		this.$el.append(this.template(this));
		this.$el.attr("color", "white");

		return this;
	},

	events: {
		"click .data-click-eatery": "ClickEatery",
	
	},

	ClickEatery: function(event){
		var self = this;
		event.preventDefault();
		console.log("Eatery has been clicked");
		console.log(self.model.eatery_id);
		var subView = new App.ModifyViewOnEatery({"model": {"eatery_id": self.model.eatery_id, "eatery_name": self.model.eatery_name, "eatery_lat": self.model.location.lat, "eatery_lng": self.model.location.lon}});	
		subView.render().el

	},

});
	
App.DisplaySuggestion = Backbone.View.extend({
	
	initialize: function(options){
		this.model = options.model;
	},

	render: function(){
		var self = this;
		if (!$.isEmptyObject(this.model.food.dishes)){
			self.$el.append('<p><a class="tooltipped col s8" data-position="right" data-delay="50" data-tooltip="If you are not looking for these dishes, please edit the dishes listed below to help us locate the desired.">Are you looking for these dishes?</a><a class="waves-effect waves-light submitButton col s4" href="#"><i class="material-icons">done_all</i>Submit</a></p>')
			$.each(this.model.food.dishes, function(iter, dish_name){
				var subView = new App.SuccessSuggestion({"model": dish_name })
				self.$el.append(subView.render().el);	
			})
		}
		else {
				self.$el.append("<p>We couldnt get you on the dishes</p>")
				var subView = new App.ErrorSuggestion()
				self.$el.append(subView.render().el);	

		}
		
		if (!$.isEmptyObject(this.model.cost)){

			var __html = " " 
			$.each(this.model.cost, function(iter, __name){
				if (iter > 0){
					__html = __html + ", " + "<i>"+ __name + "</i>"	

				}
				else{
				__html = __html + " " + "<i>"+ __name + "</i>"	
				}
			})
			self.$el.append("<p> Are you looking for" + __html + " food</p>")
		}
		else {

		}
		if (!$.isEmptyObject(this.model.service)){
			var __html = " " 
			$.each(this.model.service, function(iter, __name){
				if (iter > 0){
					__html = __html + ", " + "<i>"+ __name + "</i>"	

				}
				else{
				__html = __html + " " + "<i>"+ __name + "</i>"	
				}
			})
			self.$el.append("<p> Are you looking for" + __html + " in service </p>")

		}
		if (!$.isEmptyObject(this.model.ambience)){
			var __html = " " 
			$.each(this.model.ambience, function(iter, __name){
				if (iter > 0){
					__html = __html + ", " + "<i>"+ __name + "</i>"	

				}
				else{
				__html = __html + " " + "<i>"+ __name + "</i>"	
				}
			})
			self.$el.append("<p> Are you looking for good " + __html + " in ambience</p>")
		}
		
		this.$el.attr("style", "margin-left: auto; margin-right: auto; overflow-y: auto; height: 200px;")
		this.$('.tooltipped').tooltip({delay: 50});
		return this;

	},

	events: {
		"click .submitButton": "submitButton",
	},

	submitButton: function(event){
			var dishes_name = [];
			event.preventDefault();
			$.each($(".suggestions"), function(iter, value){
				if ($(this).val()){
					dishes_name.push($(this).val())
					}
				})
			console.log(dishes_name);
	},

});

App.SuccessSuggestion = Backbone.View.extend({
	template: window.template("success-suggestions"),
	name: function(){ return this.model.model},
	initialize: function(options){
			this.model = this.options;
			console.log(this.model);
	},
	
	render: function(){
		this.$el.append(this.template(this));
		return this;

	},

	events: {
		"mouseleave": "suggestions", 
	},
		
	suggestions: function(event){
		var self = this;
		event.preventDefault()
		if (!this.$(".suggestions").val()){
			self.$(".suggestions").hide()

		}
		/*
		console.log(this.$("#textareaSuggestions").text())
		var value = this.$("#textareaSuggestions").text()
		this.$("#textareaSuggestions").html('<textarea class="materialize-textarea">' + value + '</textarea>')  	
		*/
	},
});

App.ErrorSuggestion = Backbone.View.extend({
	template: window.template("error-suggestions"),
	className: "input-field col s12",

	render: function(){
		this.$el.append(this.template(this));
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
		var jqhr = $.post(window.eatery_details, {"eatery_id": this.model.eatery_id, "eatery_name": this.model.eatery_name})	
		jqhr.done(function(data){
			if (data.error == false){
				console.log(data.result)
				$.each(["food", "ambience", "cost", "service"], function(iter, value){
					__object = $("." + value);	
					self.makeChart(__object, data.result[value], self.model.eatery_name, value);
				})
					
				var subView = new App.ReviewForEatery({"model": {"eatery_name": self.model.eatery_name, "eatery_id": self.model.eatery_id, "eatery_address": data.result.eatery_address}})
				$("#do-review").html(subView.render().el)
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
				        plotBackgroundColor: "#263238",
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

App.ReviewForEatery = Backbone.View.extend({
	tagName: "form",
       	className: "col s12 #006064 cyan darken-4",
	template: window.template("write-review"),
	eatery_name: function(){return this.model.eatery_name},
	eatery_address: function(){return this.model.eatery_address},
	initialize: function(options){
		this.model = options.model;
		console.log(this.model.eatery_name)
		var self = this;
		},

	render: function(){
		this.$el.append(this.template(this));
		return this;

	},

	events: {
		"click .submit-review": "submitReview"},
	submitReview: function(event){
		event.preventDefault();
		console.log("Submit review clicked")
		console.log($("#submit-review-textarea").val())
		/*Api call to submit the review written by the user , The args will be the eatery id and the facebook id of the 
		 * user and obviously the review written by him or her
		 */

	
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



