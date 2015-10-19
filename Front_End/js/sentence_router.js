$(document).ready(function(){
App.Router = Backbone.Router.extend({
	initialize: function(options){
		this.el =  options.el ;
		console.log(this.el)
		var str = new App.BodyView()
	},

	routes: {
		"":  "welcome",
		"searchResult": "searchResult",
	},

	welcome: function(){
		return
		//var str = new App.WordCloudWith_D3({model: {"el": this.el}})
	},

	searchResult: function(){
		var str = new App.QueryResultView();

	},

});
App.boot = function(container){
	container = $(container);
	var router = new App.Router({el: container});
	Backbone.history.start({ pushState: true });
}
});
