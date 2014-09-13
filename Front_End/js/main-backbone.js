
$(document).ready(function(){
   	App = {} ;
	window.App = App ;
	//window.process_text_url = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/process_text";
	//window.update_model_url = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/update_model";
	window.process_text_url = "http://localhost:8000/process_text";
	window.update_model_url = "http://localhost:8000/update_model";
	window.eateries_list = "http://localhost:8000/eateries_list";
	window.eateries_details = "http://localhost:8000/eateries_details";
	window.update_review_classification = "http://localhost:8000/update_review_classification";

window.optimizely = window.optimizely || [];
window.optimizely.push(["activate"]);

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
		this.loadEateries();
		return this;
	},
	
	events: {
		"click #submitQuery": "submitQuery",
		"click #eateriesList": "changeEateryList",
		"click #loadReview": "loadReview",
		"click #updateReview": "updateReview",
		},

	updateReview: function(event){
		event.preventDefault();
		if ($("#unclassified_reviews").find('option:selected').attr('id') == null){
				bootbox.alert("Please classify review before updating it or get some common sense")
			}

		else{
		bootbox.confirm("Are you sure you want to mark this review classified?", function(result) {
			if (result == true){
				var id = $("#unclassified_reviews").find('option:selected').attr("id");
				var jqhr = $.post(window.update_review_classification, {"review_id": id})
				jqhr.done(function(data){
					bootbox.alert(data.messege);
			
			})	
			
		}})
		var str = new App.RootView()
		str.render();
		}
			
		

	},

	loadReview: function(event){
		event.preventDefault();
		console.log("load review has been clicked");
		var review_text = $("#unclassified_reviews").find('option:selected').attr('full_text')
		$("#searchQuery").val(review_text)

	},

	loadEateries: function(){
		var self = this;
		var jqhr = $.get(window.eateries_list)	
		jqhr.done(function(data){
			$.each(data.result, function(iter, eatery_dict){
				var subView = new App.EateriesListView({model: {"eatery_name": eatery_dict.eatery_name, "eatery_id": eatery_dict.eatery_id}});

				$("#eateriesList").append(subView.render().el);	
			});
		
		})
		jqhr.fail(function(){
				bootbox.alert("Either the api or internet connection is not working, Try again later")
			})
	},
	
	changeEateryList: function(event){
		event.preventDefault();
		
		$("#classified_reviews").empty();	
		$("#unclassified_reviews").empty();	
		
		var id = $("#eateriesList").find('option:selected').attr('id')
		var jqhr = $.post(window.eateries_details, {"eatery_id": id})
		
		jqhr.done(function(data){
			$.each(data.classified_reviews, function(iter, review_dict){
				var subView = new App.ClassfiedReviewsView({model: review_dict});
				$("#classified_reviews").append(subView.render().el);	
			});

			$.each(data.unclassified_reviews, function(iter, review_dict){
				var subView = new App.UnClassfiedReviewsView({model: review_dict});

				$("#unclassified_reviews").append(subView.render().el);	
			});

		});
	},

	submitQuery: function(event){
		event.preventDefault();
		$(".dynamic_display").empty()
		var jqhr = make_request($("#searchQuery").val())
		jqhr.done(function(data){
			if (data.error == false){
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


App.ClassfiedReviewsView = Backbone.View.extend({
	template: template("classified-reviews"),
	tagName: "option",
	review_text: function(){return this.model.review_text.split(" ", 10).join(" ")}, 
	review_id: function(){return this.model.review_id}, 

	initialize: function(options){
		this.model = options.model;
		console.log(this.review_text());
	},

	render: function(){
		$(this.el).attr('id', this.review_id()); 
		this.$el.append(this.template(this));
		return this;
	},
	
	events: {
		"click #classified_reviews": "change_classified_reviews",
		},
		

	change_classified_reviews: function(event){
		event.preventDefault();
		bootbox.alert("This review has already been classified")
	},	
});



App.UnClassfiedReviewsView = Backbone.View.extend({
	template: template("unclassified-reviews"),
	tagName: "option",
	full_text: function(){return this.model.review_text}, 
	review_text: function(){return this.model.review_text.split(" ", 10).join(" ")}, 
	review_id: function(){return this.model.review_id}, 

	initialize: function(options){
		this.model = options.model;
		console.log(this.review_text());
	},

	render: function(){
		$(this.el).attr('id', this.review_id()); 
		$(this.el).attr('full_text', this.full_text()); 
		this.$el.append(this.template(this));
		return this;
	},
	events: {
		"click #unclassified_reviews": "change_unclassified_reviews",
		},

	change_unclassified_reviews: function(event){
		event.preventDefault();	
		var id = $("#unclassified_reviews").find('option:selected').attr('id')
		console.log("this review has been clicked "+ id);
	},
});



App.EateriesListView = Backbone.View.extend({
	template: template("each-eatery"),
	tagName: "option",
	eatery_name: function(){return this.model.eatery_name}, 
	eatery_id: function(){return this.model.eatery_id}, 

	initialize: function(options){
		this.model = options.model;
	},

	render: function(){
		$(this.el).attr('id', this.eatery_id()); 
		this.$el.append(this.template(this));
		return this;
	},
	
});


App.RootTopView = Backbone.View.extend({
	tagName: "fieldset",
	className: "well plan",
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



