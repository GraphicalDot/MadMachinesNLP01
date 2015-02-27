
$(document).ready(function(){
window.make_request = function make_request(data, algorithm){ url =  window.process_text_url ; return $.post(url, {"text": data, "algorithm": algorithm}) }
App.RootView = Backbone.View.extend({
	//tagName: "fieldset",
	//className: "well-lg plan",
	tagName: "table",
	className: "table table-hover borderless",
	template: window.template("root"),
	
	initialize: function(){
		var self = this;
		var jqhr = $.get(window.limited_eateries_list)	
		
		jqhr.done(function(data){
			console.log(data.result)
			if (data.error == false){
				$.each(data.result, function(iter, eatery){
					var subView = new App.AppendRestaurants({"eatery": eatery});
					self.$(".append_eatery").append(subView.render().el);	
				})
						}
			else{
				bootbox.alert(data.error)	
			}
		//	self.$(".append_eatery").append('<hr><hr><tr><td></td></tr><tr><td><b>Select Sentiment</b></td></tr><tr><td><label class="checkbox"><input type="checkbox" value="1" id="positive" class="sentiment">positive</label></td></tr><tr><td><label class="checkbox"><input type="checkbox" value="0" id="negative" class="sentiment">negative</label></td></tr>')	
		})
		
		jqhr.fail(function(data){
				
				bootbox.alert(data.error)
		});
		console.log("Root view called")
		$(".side-bar").html(this.render().el);
	},

	render: function(){
		
		this.$el.append(this.template(this));
		this.$el.css({
			'height' :"200px",
			'overflow-y': "scroll", 

		})
		return this;
	},
	
	events: {
	
		"click #seeWordCloud": "seeWordCloud",
		"change .change_eatery_id": "ClickEatery",
		//"change .sentiment": "ChaneSentiment",
		},

	ChaneSentiment: function(event){
		event.preventDefault();
		var id = $(event.currentTarget).attr("id")
		console.log("id");
	},


	ClickEatery: function(event){
		event.preventDefault();
		var id = $(event.currentTarget).attr("id")
		$.each($(":checkbox"), function(iter, __checkbox){
			if (__checkbox.id != id){
				$("#" + __checkbox.id).prop("checked", false);


			}
		
		});
		
		
		console.log(id)
		if ($(":checkbox:checked").length == 1){
			//$(".sentiment").prop("checked", true)
			this.seeWordCloud(id);
		};
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


App.AppendRestaurants = Backbone.View.extend({
	template: window.template("append-restaurant"),
	tagName: "tr",
	eatery_name: function(){return this.model.eatery.eatery_name},
	eatery_id: function(){return this.model.eatery.eatery_id},
	initialize: function(options){
		this.model = this.options;
		console.log(this.eatery_name())
	},

	render: function(){
		this.$el.append(this.template(this));
		return this;	
	},


});


});



