/* global $ */
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

var vent = _.extend({}, Backbone.Events);


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
	}
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
	}
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

		range = 10;

		var jqhr = $.post(window.nearest_eateries, {"lat": this.model.eatery_lat, "long": this.model.eatery_lng, "range": range})
		jqhr.done(function(data){
			if (data.error == false){

				console.log(data.result)
				// reloadGoogleMap(self.model.eatery_lat, self.model.eatery_lng, data.result)
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
		var jqhr = $.post(window.get_trending, {"lat": this.model.eatery_lat, "lng": this.model.eatery_lng})
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
					    		effect: 'fadeInOnAppear'
					  }

				})}
				else{
					var subView = new App.ErrorView();
					$(".trending-bar-chart").html(subView.render().el);
				}
			})
			return this;
			}
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
		"click .write-review": "writeReviewfunction"
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
	}
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

	}
});


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
				out_duration: 200 // Transition out duration
				});

		$("#pickEatery").on("click", function(){
			console.log("pick eatery clicked");
			self.clickPickEatery()
				});

		$(".button-collapse").sideNav();
		// $('#modal-fblogin').openModal({
		// 		//This is for how it works options, Whihch hasnt been implemented yet
		// 		dismissible: false, // Modal can be dismissed by clicking outside of the modal
		// 		opacity: 1, // Opacity of modal background
		// 		in_duration: 300, // Transition in duration
		// 		out_duration: 200 // Transition out duration
		// 		});
		// $("#sign-in-fb").on("click", function(){
		// 	checkLoginState();
		// 		document.location.reload();
		// });

		$("#facebook_login").on("click", function(e) {
			e.preventDefault();
			$('li.user img').attr('src', 'https://lh3.googleusercontent.com/-IbvVMnLQvW4/VeU3A4n4-CI/AAAAAAAAABA/6pClgEumMW4/w140-h140-p/bleach_chibi_mugetsu_by_ultimateultimate-d4cqrw7.png');
			// $('li.user img').attr('src', "h0ttps://pixabay.com/static/uploads/photo/2015/09/05/15/13/bee-924426_640.jpg");
			$('li.user span.name').html("doof");
			$('li.user').removeClass('hidden');
			$('.sliderRow').addClass('hidden');
			$('.authRow').removeClass('hidden');
			self.render();
			// FB.login(function(response) {
			// 	document.location.reload();
			// });
		})

		$("#fbLogout").on("click", function(){
			console.log("Loggeout clicked");
			$('li.user').addClass('hidden');
			$('.sliderRow').removeClass('hidden');
			$('.authRow').addClass('hidden');
			self.render();
			// FB.logout(function(response) {
			// 	document.location.reload();
			// })

		});

		// function statusChangeCallback(response) {
		// 	console.log('statusChangeCallback');
		// 	console.log(response);
		// 	// The response object is returned with a status field that lets the
		// 	// app know the current login status of the person.
		// 	// Full docs on the response object can be found in the documentation
		// 	// for FB.getLoginStatus().
		// 	//
		// 	if (response.status === 'connected'){

		// 		FB.api('/me?fields=id,name,email, picture', function(response) {

		// 			$.post(window.users_details, {"name": response.name, "id": response.id, "email": response.email, "picture": response.picture.data.url})

		// 			$('li.user img').attr('src', response.picture.data.url);
		// 			$('li.user span.name').html(response.name);
		// 			$('li.user').removeClass('hidden');
		// 			$('.sliderRow').addClass('hidden');
		// 			$('.authRow').removeClass('hidden');
		// 			self.render()
		// 		});
        //                         // Logged into your app and Facebook
		// 		// $('#modal-fblogin').closeModal();
		// 		}
		// 		else if (response.status === 'not_authorized') {
		// 			//The person is logged into Facebook, but not your app
		// 			//document.getElementById('status').innerHTML = 'Please log ' + 'into this app.';
		// 			console.log("Fuckk you i dont want to sign in ")
		// 		}
		// 		else {
		// 			//The person is not logged into Facebook, so we're not sure if
		// 			//they are logged into this app or not.
		// 			//document.getElementById('status').innerHTML = 'Please log ' +'into Facebook.';
		// 			console.log("Not signed in ")
		// 			}
		// 		}

			// This function is called when someone finishes with the Login
			// Button.  See the onlogin handler attached to it in the sample
			// code below.
			// function checkLoginState(){
			// 	FB.getLoginStatus(function(response) {
			// 		statusChangeCallback(response);
			// 	});
			// }

		    // 	window.fbAsyncInit = function() {
			// 	FB.init({
			// 		appId      : '1605945752959547',
			// 		cookie     : true,  // enable cookies to allow the server to access // the session
			// 		xfbml      : true,  // parse social plugins on this page
			// 		version    : 'v2.4' // use version 2.4
			// 	});
			// // Now that we've initialized the JavaScript SDK, we call
			// // FB.getLoginStatus().  This function gets the state of the
			// // person visiting this page and can return one of three states to
			// // the callback you provide.  They can be:
			// //
			// // 1. Logged into your app ('connected')
			// // 2. Logged into Facebook, but not your app ('not_authorized')
			// // 3. Not logged into Facebook and can't tell if they are logged into
			// // your app or not.
			// //
			// //These three cases are handled in the callback function.

			// FB.getLoginStatus(function(response) {
			// 	statusChangeCallback(response);
			// 	});
			// FB.Event.subscribe('auth.login', function(response) {
			// 	    window.location.reload();
			// });
			// };

			$('.slider').slider({full_width: true});
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
			var latitude = position.coords.latitude;
			var longitude = position.coords.longitude
			//On the basis of the current location gets the trending dishes, mbienece, service and cost clouds
			self.callGoogleMap(latitude, longitude)
		};


			//Deals with if somebody wants to enetr a query out of which we have to figure out what he wants and a which eatery he wants
			this.intiateEnterQuery();

			//Deals with if somebdy wants to provide feedback
			this.intiateFeedback();

			//Deals with the two search bars which will have enter dish name and enter eatery name
			this.initiateAutoComplete();
			setTimeout(function() {
				$('.slider').slider({full_width: true});
			}, 100);


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
					  minLength: 4
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
				var dish_name = $(this).val();
				self.dishSuggestions(dish_name)
			});


			$('.search-eatery').typeahead({
					  hint: true,
					  highlight: true,
					  minLength: 2
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
				var eatery_name = $(this).val();
				new App.EateryDetails({"model": {"eatery_name": eatery_name}})
			})

			$('.search-eatery').bind('typeahead:select', function(ev, suggestion) {
				var eatery_name = $(this).val();
				new App.EateryDetails({"model": {"eatery_name": eatery_name}})
			});
	},


	dishSuggestions: function(dish_name){
		//Fetches relevant matched from elastic search ont he basis of the dish_name given to it
		$(".grid-dish-suggestions").html('<div class="progress"><div class="indeterminate" style="width: 70%"></div></div>')


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
					    effect: 'fadeInOnAppear'
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
								"name": $("#feedback input")[0].value
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



	callGoogleMap: function(latitude, longitude){
			var self = this;
			$(".grid-grid").html('<div class="progress"><div class="indeterminate" style="width: 70%"></div></div>')
			var jqhr = $.post(window.nearest_eateries, {"lat": latitude, "long": longitude, "range": 10})
			jqhr.done(function(data){
				console.log(data.result);
				if (data.error == false){
					self.googleMap(latitude, longitude, data.result)
					}
				else{
					var subView = new App.ErrorView();
					$(".trending-bar-chart").html(subView.render().el);
				}

			})
			var jqhr = $.post(window.get_trending, {"lat": latitude, "lng": longitude})
			$(".grid-grid").html(" ")
			jqhr.done(function(data){
				if (data.error == false){
					$.each(["food", "service", "cost", "ambience"], function(iter, category){
						$.each(data.result[category], function(iter2, model){
							console.log(model)
							model["category"] = category
							var subview = new App.DataView({"model": model})
							$(".grid-grid").append(subview.render().el);
						   })}); }
				else{
					var subView = new App.ErrorView();
					$(".trending-bar-chart").html(subView.render().el);
				}
				$(".grid-grid").gridalicious({selector: '.grid-item-new', gutter: 1, width: 150, animate: true,
					  animationOptions: {queue: true, speed: 200, duration: 300, effect: 'fadeInOnAppear'}
				})
			})




	},


	googleMap: function (__initial_lat, __initial_long, eateries_list){
		       		var self = this;
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
								{"hue": "#E2DA99"}]
						}],
					draggable: true

			};
			var map = new google.maps.Map(mapCanvas, mapOptions)
			marker = new google.maps.Marker({position: new google.maps.LatLng(__initial_lat, __initial_long),
				map: map,
				icon: 'css/location-icon.png'});

			//Making  circle of radiu 1km around the center of the google maps
			//Then map.fitBounds will be called so that the center will fit the google map div
			var circleSettings = {strokeColor: '#4EB1BA', strokeOpacity: 0.8, strokeWeight: 2, fillColor: '#4EB1BA', fillOpacity: 0.35,
				      map: map, center:  new google.maps.LatLng(__initial_lat, __initial_long), radius: 1000 };
			circle = new google.maps.Circle(circleSettings);
			map.fitBounds(circle.getBounds());


			//Setting the traffic layer for the google map so that the used in effect will have a clear idea about the
			//Fucking traffic scenario
			var trafficLayer = new google.maps.TrafficLayer();
			trafficLayer.setMap(map);

			var infowindow = new google.maps.InfoWindow({
			    content: ""
			  });

			//Adding infobox for each eatery present in the eateries_list
			$.each(eateries_list, function(iter, data){
                                marker = new google.maps.Marker({
                                map: map,
                                position: new google.maps.LatLng(data.eatery_coordinates[0], data.eatery_coordinates[1]),
                                title: data.eatery_name,
				eatery_id: data.eatery_id,
				address: data.eatery_address,
				html: "<div id='infobox'>" + data.eatery_name + "</br>" + data.eatery_address + "</div>"

                                })
                                //Mouse over event for every eatery, so on mouse over the infowindow will show
				//The address and name of the eatery.
				google.maps.event.addListener(marker, 'mouseover', function() {
					infowindow.setContent(this.get("html"));
					infowindow.open(map, this);
					});

				//MOuseout event for the infowindow
				google.maps.event.addListener(marker, 'mouseout', function() {
					infowindow.close();
					});

				//CLick event for the maker, so if a user want to checkout the details of the eatery
				//then he can click on the eatery to change the woed cloud
				google.maps.event.addListener(marker, 'click', function() {
					console.log(this.get("eatery_id"));
				     	var subView = new App.EateryDetails({"model": {"eatery_id": this.get("eatery_id"), "eatery_name": this.get("title")}});
					//subView.render().el;
					});
                        	})//loop for eatery completed

		       		google.maps.event.addListener(map, 'click', function(event) {
					var latitude = event.latLng.lat()
					var longitude = event.latLng.lng()
					self.callGoogleMap(latitude, longitude);
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
			var tempData= {"ambience":["ambience-overall"],"food":{"dishes":["pita bread"]},"cost":["expensive","value for money"],"service":["service-overall"],"sentences":{"food":["but the \" pita bread \" is roomali roti .","dishes","but as a side for dips , it doesn't make the cut .","null-food"],"ambience":["the hummus and baba ganoush are great , excellent value for money .","ambience-overall","takeaway service was prompt .","ambience-null","but the \" pita bread \" is roomali roti .","ambience-null","there's no excuse for this , given the countless places providing at least a better attempt at pita bread ( i e","ambience-overall",".","ambience-null","fluffier , more substantial ) , not only in Delhi","ambience-null","but even in smaller cities in India .","ambience-null","i'm sure it's great for wraps ,","ambience-null","but as a side for dips , it doesn't make the cut .","ambience-null","i would rather pay slightly higher prices and get decent bread .","ambience-null"],"cost":["the hummus and baba ganoush are great , excellent value for money .","value for money","i would rather pay slightly higher prices and get decent bread .","expensive"],"overall":["i'm sure it's great for wraps ,","overall"],"service":["takeaway service was prompt .","service-overall"]}};
			var subView = new App.DisplaySuggestion({"model": tempData});
			$(".queryResult").html("");
						$(".queryResult").append(subView.render().el);
		});
			}
			}}
		      );
		}
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
		"click .data-click-eatery": "ClickEatery"

	},

	ClickEatery: function(event){
		var self = this;
		event.preventDefault();
		console.log("Eatery has been clicked");
		console.log(self.model.eatery_id);
		var subView = new App.ModifyViewOnEatery({"model": {"eatery_id": self.model.eatery_id, "eatery_name": self.model.eatery_name, "eatery_lat": self.model.location.lat, "eatery_lng": self.model.location.lon}});
		subView.render().el

	}

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
	totalpositive : function(){return this.model.positive + this.model.superpositive},
	totalnegative : function(){return this.model.negative + this.model.supernegative},
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
		"click .data-click-eatery": "ClickEatery"

	},

	ClickEatery: function(event){
		var self = this;
		event.preventDefault();
		var subView = new App.ModifyViewOnEatery({"model": {"eatery_id": self.model.eatery_id, "eatery_name": self.model.eatery_name, "eatery_lat": self.model.location.lat, "eatery_lng": self.model.location.lon}});
		subView.render().el

	}

});

App.DisplaySuggestion = Backbone.View.extend({

	initialize: function(options){
		this.model = options.model;
		vent.on('remove-suggestion', this.removeSuggestion, this);
	},

	removeSuggestion: function(el) {
		$(el).closest('li').remove();
		$('.collapsible').collapsible();
	},

	render: function(){
		var self = this;
		if (!$.isEmptyObject(this.model.food.dishes)){
			self.$el.append('<div class="col s12"><i class="material-icons close_display">add</i><p><a class="tooltipped col s8" data-position="right" data-delay="50" data-tooltip="If you are not looking for these dishes, please edit the dishes listed below to help us locate the desired.">Are you looking for these dishes?</a></p></div><div class="divider">');
			self.$el.append('<div class="col s8" style="position:relative;"><ul class="collapsible" data-collapsible="accordion"></ul></div>');
			self.$el.append('<div class="col s4" style="margin: 0.5rem 0 1rem 0;"><a class="add-more-suggestion waves-effect waves-light btn left"><i class="material-icons left">add</i>Add More</a><a class="btn left waves-effect waves-light submitButton" name="action" type="submit" style="margin: 0 10px!important;"><i class="material-icons left">done_all</i>Submit</a></div>');
			$.each(this.model.food.dishes, function(iter, dish_name){
				var subView = new App.SuccessSuggestion({"model": {"dish_name": dish_name }});
				self.$el.find('ul').append(subView.render().el);
			});
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
			self.$el.append("<div class='col s12'><p> Are you looking for" + __html + " food</p></div>")
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
			self.$el.append("<div class='col s12'><p> Are you looking for" + __html + " in service </p></div>")

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
			self.$el.append("<div class='col s12'><p> Are you looking for good " + __html + " in ambience</p></div>")
		}

		this.$el.attr("style", "margin-left: auto; margin-right: auto; overflow-y: auto; height: auto;")
		this.$('.tooltipped').tooltip({delay: 50});

		setTimeout(function() {
		 	$('.collapsible').collapsible({
				 accordion: true
			 });
		}, 100);
		this.delegateEvents();
		return this;

	},

	events: {
		"click .submitButton": "submitButton",
		"click .add-more-suggestion": "addMoreSuggestion",
		"click i.delete": "removeSuggestion",
		"click i.close_display": "removeView"
	},

	addMoreSuggestion: function() {
		var subView = new App.SuccessSuggestion({"model": {"dish_name": "" }});
		this.$el.find('ul').append(subView.render().el);
		$('.collapsible').collapsible();
		// $('ul.collapsible').append('<li><div class="collapsible-header"><input placeholder="enter your idea here.." type="text" class="suggestions col s10" value=""><i class="material-icons open right">send</i><i class="material-icons delete right">delete</i></div></li>');
		return this;
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
	removeView: function(evt) {
		evt.preventDefault();
		this.remove();
	}

});

App.SuccessSuggestion = Backbone.View.extend({
	tagName: 'li',
	template: window.template("success-suggestions-2"),
	name: function(){ return this.model.dish_name},
	initialize: function(options){
			this.model = options.model;
			console.log(this.model);
	},

	render: function(){
		this.$el.append(this.template(this));

		return this;

	},

	events: {
		"mouseleave": "suggestions",
		"click i.delete": "deleteSuggestion",
		"click .collapsible-header": "headerClicked",
		"click input": "headerClicked",
		"click i.open": "openAccordion",
		"click i.close": "closeAccordion"

	},

	headerClicked: function(e) {
		console.log('hey');
		$(e.currentTarget).closest('li').removeClass('active').find('.collapsible-header').removeClass('active');
		e.preventDefault();
		e.stopPropagation();
	},

	deleteSuggestion: function(e) {
		e.preventDefault();
		// console.log(e);
		var userAnswer= confirm("Are you sure you want to delete?");
		if(userAnswer) {
			vent.trigger('remove-suggestion', e.currentTarget);
		}
	},

	openAccordion: function(e) {
		console.log("eventbinding");
		// e.stopPropagation();
		var el= $(e.currentTarget);
		console.log("Opening Accordion");

		el.closest('li').find('.collapsible-header').after('<div class="collapsible-body"><p>Lorem ipsum dolor sit amet.</p></div>');
		$('.collapsible').collapsible();
		// <div class="collapsible-body"><p>Lorem ipsum dolor sit amet.</p></div>
		el.closest('li').trigger('click');
		el.removeClass('open').addClass('close');
	},

	closeAccordion: function(e) {
		console.log("Closeing ACcordion");
		// e.stopPropagation();
		var el= $(e.currentTarget);
		if(el.closest('li').find('.collapsible-body').length) {
			el.closest('li').find('.collapsible-body').remove();
		}

		$('.collapsible').collapsible();

		el.closest('li').trigger('click');
		el.removeClass('close').addClass('open');
	},

	suggestions: function(event){
		var self = this;
		event.preventDefault()
		if (!this.$(".suggestions").val()){
			// self.$(".suggestions").hide()

		}
		/*
		console.log(this.$("#textareaSuggestions").text())
		var value = this.$("#textareaSuggestions").text()
		this.$("#textareaSuggestions").html('<textarea class="materialize-textarea">' + value + '</textarea>')
		*/
	}
});

App.ErrorSuggestion = Backbone.View.extend({
	template: window.template("error-suggestions"),
	className: "input-field col s12",

	render: function(){
		this.$el.append(this.template(this));
		return this;
	}
});




App.EateryDetails = Backbone.View.extend({
	initialize: function(options){
		var self = this;
		this.model = options.model;

		console.log("Called from Eatery details");
		console.log(this.model.eatery_id);
		console.log(this.model.eatery_name);

		if (!self.model.eatery_id){
			console.log("Called without eatery id");
			self.renderOnEateryName();


		}
		else {
			self.render()

		}


	},

	renderOnEateryName: function(){
		var self = this;
		var jqhr = $.post(window.get_eatery, {"eatery_name": this.model.eatery_name, "type_of_data": "highchart"})
		jqhr.done(function(data){
			if (data.error == false){
				console.log(data.result)
				// $.each(["food", "ambience", "cost", "service"], function(iter, value){
				// 	__object = $("." + value);
				// 	self.makeChart(__object, data.result[value], self.model.eatery_name, value);
				// })
				self.makeD3Chart(data);

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
	render: function(){
		var self = this;
		var jqhr = $.post(window.eatery_details, {"eatery_id": this.model.eatery_id, "eatery_name": this.model.eatery_name, "type_of_data": 'highchart'})
		jqhr.done(function(data){
			if (data.error == false){
				// console.log(data.result)
				self.makeD3Chart(data);
				// $.each(["food", "ambience", "cost", "service"], function(iter, value){
				// 	self.makeD3Chart(data.result[value], self.model.eatery_name, value);
				// 	// self.makeChart(__object, data.result[value], self.model.eatery_name, value);
				// })

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

	makeD3Chart: function(data, name, type) {
		$(".eateryDetails .card-panel").empty();
		$(".eateryDetails").show();
		function doTheThing(input) {
		if (input.success) {
			// var main_keys= ['food'];
			var main_keys = ['food', 'ambience', 'cost', 'service'];

			for (var i = 0; i < main_keys.length; i++) {
				(function (current_main_key) {
					var max_total = 0;
					var chart_categories = input.result[current_main_key].categories;
					var chart_series = input.result[current_main_key].series;

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
					console.log(chart_data);
					radialLineChartD3(chart_data, current_main_key, max_total);
				})(main_keys[i]);
			}
		}
		// return output;
	}
	doTheThing(data);

	},

	makeChart: function(__object,  __data, eatery_name, category){

		console.log(__data.categories);

			__object.highcharts({

				chart: {
						renderTo: 'container',
				        type: 'bar',
				        alignTicks: false,
				        plotBackgroundColor: "#263238",
				        plotBackgroundImage: null,
				        plotBorderWidth: 2,
				        plotShadow: false
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
						// labels: {
						// 	"step": 1,
						// 		"rotation": 0,
						// },
						// tickInterval: 1,
					},
				yAxis: {
						min: 0,
						title: {
							text: 'total frequency'
						},
						lineColor: '#339',
						tickColor: '#339',
						minorTickColor: '#339',
						// labels: {
						// 	"step": 1,
						// 	"rotation": 0,
						// },
						// tickInterval: 1
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
		}

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


	}
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
	}

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
	}

	})

});
