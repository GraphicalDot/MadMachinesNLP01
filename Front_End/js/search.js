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
	//tagName: "fieldset",
	//className: "well-lg plan",
	template: window.template("root"),
	initialize: function(){
		var self = this;
		/*
		
		$(".side-bar").html(this.render().el);
			*/
		},

	render: function(){
		this.beforeRender();	
		this.$el.append(this.template(this));
		return this;
	},

	beforeRender: function(){
		var subview = new App.TrendingView();
		subview.render().el;
	},
	
	events: {
		'keyup': 'processKey', 	
		},


	processKey: function(event){
		event.preventDefault();
		if(event.which === 13){
			value = $("#searchQuery").val();
			if (value == ""){
				console.log("No result");
			}
		var jqhr = $.post(window.resolve_query, {"text": value})	
		jqhr.done(function(data){
			if (data.error == false){
				console.log(data.result)
				var subView = new App.BarChartView();
				subView.render().el;	
								
				/*
				$.each(data.result, function(iter, eatery){
					var subView = new App.AppendRestaurants({"eatery": eatery});
					self.$(".append_eatery").append(subView.render().el);	
				*/
					}
			else{
				bootbox.alert(data.error)	
			}
		})
		
		jqhr.fail(function(data){
				
				bootbox.alert(data.error)
		});
		}
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


});



