$(document).ready(function(){
App.Router = Backbone.Router.extend({
	initialize: function(options){
		this.el =  options.el ;
	},

	routes: {
		"":  "welcome",
	},
	
	welcome: function(){
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
