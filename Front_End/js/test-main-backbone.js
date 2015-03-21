
$(document).ready(function(){
window.make_request = function make_request(data, algorithm){ url =  window.process_text_url ; return $.post(url, {"text": data, "algorithm": algorithm}) }
App.RootView = Backbone.View.extend({
	//tagName: "fieldset",
	//className: "well-lg plan",
	tagName: "table",
	className: "table table-striped root-table",
	template: window.template("root"),
	
	initialize: function(){
		var self = this;
		console.log("Root view called")

	},

	render: function(){
		
		this.$el.append(this.template(this));
		
		return this;
	},
	
	events: {
	

		"click #submit": "submit",
		},


	submit: function(event){
		$(".main-body").empty()
		event.preventDefault();
		bootbox.dialog({
			closeButton: false, 
			message: "<img src='css/images/loading__a.gif'>",
			className: "loadingclass",
		}); 

		console.log("submit button cliked")
		text = $("#searchQuery").val()
		var jqhr = $.post(window.raw_text_processing, {"text": text})

		 jqhr.done(function(data){
			 var subView = new App.WordCloudWith_D3({model: data.result});
			 $(".loadingclass").modal("hide");
		 });
		jqhr.fail(function(){
			bootbox.alert("Either the api or internet connection is not working, Try again later")
			self.$el.removeClass("dvLoading"); 
			event.stopPropagation();
		});
		//var algorithm = $("#appendAlgorithms").find("option:selected").val()
		//this.processText(algorithm)
	},


});


});



