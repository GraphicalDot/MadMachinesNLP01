
$(document).ready(function(){
   	App = {} ;
	window.App = App ;
	window.URL = "http://localhost:8000/"
	//window.URL = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/"
	
	window.process_text_url = window.URL + "process_text";
	window.update_model_url = window.URL + "update_model";
	window.update_review_error = window.URL + "update_review_error";
	window.update_customer = window.URL + "update_customer";
	window.eateries_list = window.URL + "eateries_list";
	window.eateries_details = window.URL + "eateries_details";
	window.update_review_classification = window.URL + "update_review_classification";
	window.get_ngrams = window.URL + "get_ngrams";
	window.upload_noun_phrases = window.URL + "upload_noun_phrases";
	window.upload_interjection_error = window.URL + "upload_interjection_error";
	
	/*
	window.process_text_url = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/process_text";
	window.update_model_url = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/update_model";
	window.eateries_list = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/eateries_list";
	window.eateries_details = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/eateries_details";
	window.update_review_classification = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/update_review_classification";
	window.update_review_error = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/update_review_error";
	window.update_customer = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/update_customer";
	window.get_ngrams = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/get_ngrams";
	window.upload_noun_phrases = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/upload_noun_phrases";
	*/


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
	className: "well-lg plan",
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
			$("#searchQuery").val(" ");		
			$(".dynamic_display").empty();
			}
		})
		}
	},

	loadReview: function(event){
		event.preventDefault();
		console.log("load review has been clicked");
		var review_text = $("#unclassified_reviews").find('option:selected').attr('full_text')
		var review_id = $("#unclassified_reviews").find('option:selected').attr('id')
		$("#searchQuery").val(review_text)
		$("#searchQuery").attr('review_id', review_id); 

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

		var id = $("#searchQuery").attr("review_id")
		var jqhr = make_request($("#searchQuery").val())
		jqhr.done(function(data){
			if (data.error == false){
				var subView = new App.RootTopView({model: {"sentiment": data.overall_sentiment, "phrases": data.noun_phrase}})
				$(".dynamic_display").append(subView.render().el);	
				$(".dynamic_display").append("<fieldset class='well'><div class='span5'><p style='text-align: center'><b>Sentence</b></p></div><div class='span1'><p style='text-align: center'><b>Polarity</b></p></div><div class='span1'><p style='text-align: center'><b>tag</b></p></div><div class='span1'><p style='text-align: center'><b>Sentiment</b></p></div><div class='span1'><p style='text-align: center'><b>Customer</b></p></div><div class='span1'><p style='text-align: center'><b>Error</b></p></div><div class='span1'><p class='pull-left' style='text-align: center'><b>Noun Pharses</b></p></div></fieldset>")
				$.each(data.result, function(iter, text){
					var subView = new App.RootRowView({model: {"text": text, "review_id": id}});
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
	noun_phrases: function(){return this.model.text.noun_phrases},
	polarity_name: function(){return this.model.text.polarity.name},
	polarity_value: function(){return this.model.text.polarity.value},
	sentence: function(){return this.model.text.sentence},
	review_id: function(){ return this.model.review_id},
	tag: function(){return this.model.text.tag},
	
	initialize: function(options){
		this.values = {"food": 1, "service": 2, "ambience": 3, "cost": 4, "null": 5, "overall": 6};
		this.polarity_tag = {"positive": 1, "negative": 2,};
		console.log(this.sentence() + this.polarity_tag[this.polarity_name()] + this.polarity_value() + this.polarity_name());
		this.model = options.model;
	},
	
	render: function(){
		this.$el.append(this.template(this));
		this.$("#ddpFilter option[value='" + this.values[this.tag()] + "']").attr("selected", "selected")
		this.$("#ddpFiltersentiment option[value='" + this.polarity_tag[this.polarity_name()] + "']").attr("selected", "selected")
		return this;
	},

	events: {
		    "change #ddpFilter" : "changeTag",
		    "change #ddpFiltersentiment" : "changeSentiment",
		    "change #ddpFilterError" : "changeError",
		    "change #ddpFilterCustomer" : "changeCustomer",
		    "change #ddpFilterWordCloud" : "uploadWordCloud",
	},


	uploadWordCloud: function(event){
		var self = this;
		event.preventDefault()
		sentence = self.sentence();
		grams = self.$('#ddpFilterWordCloud option:selected').text();
		var jqhr = $.post(window.get_ngrams, {"text": sentence, "grams": grams})	
		jqhr.done(function(data){
			if (data.success == true){
					var subView = new App.NgramsParent({model: {"result": data.result, "sentence": sentence, "grams": grams, parent: self}});
					self.$el.after(subView.render().el);	
			}
			else {
				bootbox.alert(data.messege)
			}	
		})
				
		jqhr.fail(function(){
			bootbox.alert("Either the api or internet connection is not working, Try again later")
			})
	},

	changeSentiment: function(event){
		var self = this;
		event.preventDefault()
		bootbox.confirm("Are you sure you want to change the polarity of this sentence?", function(result) {
			if (result == true){
				sentence = self.sentence();
				changed_polarity = self.$('#ddpFiltersentiment option:selected').text();
				var jqhr = $.post(window.update_model_url, {"text": sentence, "tag": changed_polarity, "review_id": self.review_id()})	
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
	
	changeError: function(event){
		/**********/
		//Take care of the interjection tag present in the database, add it to the backend
		/*********/
		var self = this;
		event.preventDefault()
				
		error = self.$('#ddpFilterError option:selected').val();
		
		if (error == 2){
		bootbox.prompt("Please enter error messege", function(error_messege) {                
			if (error_messege != null) {                                             
				
				sentence = self.sentence();
				error = self.$('#ddpFilterError option:selected').val();
				var jqhr = $.post(window.update_review_error, {"sentence": sentence, "is_error": error, "review_id": self.review_id(),"error_messege": error_messege})	
				jqhr.done(function(data){
					console.log(data.success)
					if (data.success == true){
						bootbox.alert(data.messege)
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
		}
		else {
			sentence = self.sentence();
			interjection = self.$('#ddpFilterError option:selected').val();
			var jqhr = $.post(window.upload_interjection_error, {"sentence": sentence, "is_error": error, "review_id": self.review_id(),})	
			jqhr.done(function(data){
				console.log(data.success)
				if (data.success == true){
					bootbox.alert(data.messege)
					}
				else {
					bootbox.alert(data.messege)}	
				})
				
			jqhr.fail(function(){
				bootbox.alert("Either the api or internet connection is not working, Try again later")})
				
		}	
	},
	
	
	changeCustomer: function(event){
		var self = this;
		event.preventDefault()
		bootbox.confirm("Are you sure you want to mark this sentece as repeated customer sentence", function(result) {
			if (result == true){
				sentence = self.sentence();
				customer = self.$('#ddpFilterCustomer option:selected').val();
				var jqhr = $.post(window.update_customer, {"text": sentence, "is_repeated": customer, "review_id": self.review_id()})	
				jqhr.done(function(data){
					console.log(data.success)
					if (data.success == true){
						bootbox.alert("This sentence has been marked as repeated customer review, Yo Yo honey singh!!")
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

				var jqhr = $.post(window.update_model_url, {"text": sentence, "tag": changed_tag, "review_id": self.review_id()})	
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

App.NgramsParent = Backbone.View.extend({
	tagName: "fieldset",
	className: "well",
	template: template("ngrams-parent"),
	sentence: function(){ return this.model.sentence},
	block_gram: function(){ return this.model.grams},
	review_id: function(){ return this.model.parent.review_id()},
	initialize: function(options){
		this.model = options.model;
	},

	render: function(){
		var self = this;
		$.each(this.model.result, function(iter, text){ 
			var subView = new App.Ngrams({model: {"text": text, "sentence": sentence, parent: self}});
			self.$el.append(subView.render().el);
		})
		this.$el.append(this.template(this));
		return this;
	},

	events: {
		"click #hide": "hide",
		},
	hide: function(event){
		event.preventDefault();
		console.log("hide has been clicked" + this.sentence());
		this.$el.hide();
	},



});


App.Ngrams = Backbone.View.extend({
	
	template: template("ngram"),
	noun_phrase: function(){return this.model.text},
	sentence: function(){ return this.model.sentence},
	initialize: function(options){
		this.model = options.model;

	},
	render: function(){
		this.$el.append(this.template(this));
		return this;
	},
	
	events: {
		"click #submitCloud": "submitCloud",

	},

	submitCloud: function(event){
		console.log(this.model.parent.review_id());
		event.preventDefault();
		var self = this;
		console.log(this.noun_phrase(), this.sentence());
		var jqhr = $.post(window.upload_noun_phrases, {"noun_phrase": self.noun_phrase(), "review_id": self.model.parent.review_id(), "sentence": self.model.parent.sentence()})	
		jqhr.done(function(data){
			if (data.success == true){
				bootbox.alert(data.messege)
			}
			else {
				bootbox.alert(data.messege)
			}	
			})
				
		jqhr.fail(function(){
				bootbox.alert("Either the api or internet connection is not working, Try again later")
			})	
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



