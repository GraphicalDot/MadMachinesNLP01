
$(document).ready(function(){
   	App = {} ;
	window.App = App ;
	window.process_text_url = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/process_text";
	window.update_model_url = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/update_model";
	//window.process_text_url = "http://localhost:8000/process_text";
	//window.update_model_url = "http://localhost:8000/update_model";

function make_request(data){
	url =  window.process_text_url ;
	console.log(window.url)
	return 	$.post(url, {"text": data})
		}

/*This is the template object which uses name as an argument to return handlebar compiled template from the the html
 */
var template = function(name){
    return Mustache.compile($("#"+name+"-template").html());
};



App.RootView = Backbone.View.extend({
	tagName: "fieldset",
	className: "well plan",
	template: template("root"),
	initialize: function(){
		console.log("Root view called")
	},
	render: function(){
		this.$el.append(this.template(this));
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
				var subView = new App.RootTopView({model: {"sentiment": data.overall_sentiment, "phrases": data.noun_phrase}})
				$(".dynamic_display").append(subView.render().el);	
				$.each(data.result, function(iter, text){
					var subView = new App.RootRowView({model: text});
					$(".dynamic_display").append(subView.render().el);	
				})
						}
			else{
				bootbox.alert(data.messege)	
			}
			})
		jqhr.fail(function(){
				bootbox.alert("Either the api or internet connection is not working, Try again later")
			})
		
	},
});

App.RootTopView = Backbone.View.extend({
	tagName: "fieldset",
	className: "well",
	template: template("root-top"),

	phrases: function(){return this.model.phrases},
	sentiment: function(){return this.model.sentiment},
	
	initialize: function(options){
		this.model = options.model;
	},
	render: function(){
		var self = this;
		this.$el.append(this.template(this));
		$(this.model.phrases).each(function(index, value){
				self.subView = new App.NounPhraseView({model: value});
				self.$("#tagcloud").append(self.subView.render().el);	
				self.$("#tagcloud").append('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');	
		})

		this.afterRender();
		return this;
	},
		
	afterRender: function(){
		this.$("#tagcloud a").tagcloud({
			size: {
				start: 10,
				end: 25,
				unit: 'px'},
			color: {
				start: "#CDE",
				end: "#FS2",}
				})
			},
});

App.NounPhraseView = Backbone.View.extend({
	template: Mustache.compile('{{nounPhrase}}'),
	tagName: "a",
	items: Array(5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20),
	size: function(){return this.items[Math.floor(Math.random()*this.items.length)] },
	nounPhrase: function(){return this.model},

	initialize: function(options){
		this.model = options.model;
		console.log(this.size())
	},

	render: function(){
		this.$el.append(this.template(this));
		this.afterRender();
		return this;
	},

	afterRender: function(){
		this.$el.attr({href: "#", rel: this.size()});
	},

});


App.RootRowView = Backbone.View.extend({
	tagName: "fieldset",
	className: "well plan",
	template: template("root-row"),
	noun_phrases: function(){return this.model.noun_phrases},
	polarity_name: function(){return this.model.polarity.name},
	polarity_value: function(){return this.model.polarity.value},
	sentence: function(){return this.model.sentence},
	tag: function(){return this.model.tag},
	
	initialize: function(options){
		this.values = {"food": 1, "service": 2, "ambience": 3, "cost": 4, "null": 5, "overall": 6};
		this.polarity_tag = {"positive": 1, "negative": 2,};
		console.log(this.sentence() + this.polarity_tag[this.polarity_name()] + this.polarity_value() + this.polarity_name());
		this.model = options.model;
	},
	
	render: function(){
		this.$el.append(this.template(this));
		this.$("#ddpFilter option[value='" + this.values[this.model.tag] + "']").attr("selected", "selected")
		this.$("#ddpFiltersentiment option[value='" + this.polarity_tag[this.polarity_name()] + "']").attr("selected", "selected")
		return this;
	},

	events: {
		    "change #ddpFilter" : "changeTag",
		    "change #ddpFiltersentiment" : "changeSentiment",
	},

	changeSentiment: function(event){
		var self = this;
		event.preventDefault()
		bootbox.confirm("Are you sure you want to change the polarity of this sentence?", function(result) {
			if (result == true){
				sentence = self.sentence();
				changed_polarity = self.$('#ddpFiltersentiment option:selected').text();
				var jqhr = $.post(window.update_model_url, {"text": sentence, "tag": changed_polarity})	
				jqhr.done(function(data){
					console.log(data.success)
					if (data.success == true){
						bootbox.alert("Polarity has been changed")
						}
					else {
						bootbox.alert(data.messege)
					}	
				})
				
				jqhr.fail(function(){
					bootbox.alert("Either the api or internet connection is not working, Try again later")
				})
				}	
		}); 
	},
	changeTag: function(event){
		var self = this;
		event.preventDefault()
		bootbox.confirm("Are you sure you want to change the tag of this sentence?", function(result) {
			if (result == true){
				changed_tag = self.$('#ddpFilter option:selected').text();
				sentence = self.sentence();

				var jqhr = $.post(window.update_model_url, {"text": sentence, "tag": changed_tag})	
				jqhr.done(function(data){
					console.log(data.success)
					if (data.success == true){
						bootbox.alert("Tag has been changed")
						}
					else {
						bootbox.alert(data.messege)
					}	
				})
				
				jqhr.fail(function(){
					bootbox.alert("Either the api or internet connection is not working, Try again later")
				})
			
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



