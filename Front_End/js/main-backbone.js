
$(document).ready(function(){
   	App = {} ;
	window.App = App ;


function make_request(data){
	console.log(data)
	url =  "http://localhost:8000/v1/process_text" ;
	$.ajaxSetup({
		beforeSend: function(xhr){
			 xhr.setRequestHeader("Content-Type", "application/json");
		}});

	return 	$.ajax({
		url: url,
		type: "POST",
		data: data,
		dataType: 'json',
  		async: false,
	});
		}

/*This is the template object which uses name as an argument to return handlebar compiled template from the the html
 */
var template = function(name){
    return Mustache.compile($("#"+name+"-template").html());
};



App.RootView = Backbone.View.extend({
	tagName: "form",
	className: "form-horizontal",
	template: template("root"),
	initialize: function(){
		console.log("Root view called")
	},
	render: function(){
		this.$el.append(this.template(this));
		console.log( this.el)
		return this;
	},
	events: {
		"click #submitQuery": "submitQuery",
	},

	submitQuery: function(event){
		event.preventDefault();
		$(".dynamic_display").empty()
		var jqhr = make_request($("#searchQuery").val())
		jqhr.done(function(data){
			if (data.error == false){
				var subView = new App.RootErrorRowView({model: data.data_head})
				$(".dynamic_display").append(subView.render().el);	
				$.each(data.data, function(iter, text){
					var subView = new App.RootRowView({model: text});
					$(".dynamic_display").append(subView.render().el);	
				})
						}
			else{
				bootbox.alert(data.messege)	
				var subView = new App.RootErrorRowView({model: data.data})
				$(".dynamic_display").append(subView.render().el);	
			}
			})
	},
});

App.RootRowView = Backbone.View.extend({
	tagName: "form",
	className: "form-horizontal",
	template: template("root-row"),
	actualDate: function(){return this.model.actual_date},
	text: function(){return this.model.text},
	initialize: function(options){
		this.model = options.model;
	},
	render: function(){
		this.$el.append(this.template(this));
		return this;
	},
});
App.RootErrorRowView = Backbone.View.extend({
	tagName: "form",
	className: "form-horizontal",
	template: template("root-row-error"),
	text: function(){return this.model.data_tag},
	imageSrc: function(){return this.model.image_src},
	initialize: function(options){
		this.model = options.model;
	},
	render: function(){
		this.$el.append(this.template(this));
		return this;
	},
});



App.Router = Backbone.Router.extend({
	initialize: function(options){
		this.el =  options.el ;
	},

	routes: {
		"":  "welcome",
	},
	
	welcome: function(){
		console.log("Home view calledd")
		var str = new App.RootView()
		this.el.html(str.render().el);
	},
});

App.boot = function(container){
	container = $(container);
	var router = new App.Router({el: container});
	Backbone.history.start();
}
});



