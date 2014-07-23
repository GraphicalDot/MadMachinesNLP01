
$(document).ready(function(){
   	App = {} ;
	window.App = App ;


function make_request(data){
	console.log(data)
	url =  "http://localhost:8000/process_text" ;
	console.log(JSON.stringify({"text": data}))

	return 	$.post(url, {"text": data})
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
				data.overall_sentiment
				data.result
				$.each(data.result, function(iter, text){
					var subView = new App.RootRowView({model: text});
					$(".dynamic_display").append(subView.render().el);	
				})
						}
			else{
				bootbox.alert(data.messege)	
				//var subView = new App.RootErrorRowView({model: data.data})
				//$(".dynamic_display").append(subView.render().el);	
			}
			})
	},
});

App.RootRowView = Backbone.View.extend({
	tagName: "fieldset",
	className: "well",
	template: template("root-row"),

	noun_phrases: function(){return this.model.noun_phrases},
	polarity: function(){return this.model.polarity},
	sentence: function(){return this.model.sentence},
	tag: function(){return this.model.tag},
	initialize: function(options){
		this.model = options.model;
	},
	render: function(){
		console.log(this.sentence())
		this.$el.append(this.template(this));
		this.$('#ddpFilter option:selected').text(this.model.tag)
		return this;
	},

	events: {
		    "change #ddpFilter" : "changeTag"
	},

	changeTag: function(event){
		event.preventDefault()
		console.log(this.$('#ddpFilter option:selected').text())
		bootbox.confirm("Are you sure?", function(result) {
			if (result == true){
				console.log("value changed");
			}	
		}); 
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



