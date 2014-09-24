
$(document).ready(function(){

App.RootView = Backbone.View.extend({
	//tagName: "fieldset",
	//className: "well-lg plan",
	tagName: "table",
	className: "table table-striped root-table",
	template: window.template("root"),
	
	initialize: function(){
		console.log("Root view called")

	},

	render: function(){
		this.$el.append(this.template(this));
		return this;
	},
	
	events: {
		"click #submitQuery": "submitQuery",
		"click #eateriesList": "changeEateryList",
		"click #loadReview": "loadReview",
		"click #updateReview": "updateReview",
		"click #countReviews": "countReviews",
		"click #citiesList": "loadEateriesForCity",
		},

	countReviews: function(event){
		event.preventDefault();
		$(".reviewsCount").empty();
		if ($('.count-table').is(':empty')){
			console.log("yo yo honey singh");	  
		}
		var self = this;
		var jqhr = $.get(window.get_reviews_count)	
		jqhr.done(function(data){
				var subView = new App.ReviewsCountParentView({model: {"data": data.result} });
				bootbox.dialog({
					"title": "Total number of reviews",
					"message": subView.render().el,
					"show": true,	
					"animate": true,
					"closeButton": true,
					});
		$("table").tablecloth({
			  theme: "default",
		  bordered: true,
		  condensed: true,
		  striped: true,
		  sortable: true,
		  clean: true,
		  cleanElements: "th td",
		  customClass: "root-table"
		});
		$(".root-table").tablesorter(); 	
		});
		
		jqhr.fail(function(){
				bootbox.alert("Either the api or internet connection is not working, Try again later")
			})

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

	loadEateriesForCity: function(){
		$("#eateriesList").empty();	
		var self = this;
		var city = $("#citiesList").find('option:selected').text()
		console.log(city)
		var jqhr = $.post(window.eateries_list, {"city": city})	
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
		var jqhr = window.make_request($("#searchQuery").val())
		jqhr.done(function(data){
			if (data.error == false){
				var subView = new App.RootTopView({model: {"sentiment": data.overall_sentiment, "phrases": data.noun_phrase}})
				$(".dynamic_display").append(subView.render().el);	
				$(".dynamic_display").append("<fieldset class='well'><div class='span5'><p style='text-align: center'><b>Sentence</b></p></div><div class='span1'><p style='text-align: center'><b>Tag</b></p></div><div class='span1'><p style='text-align: center'><b>Polarity</b></p></div><div class='span1'><p style='text-align: center'><b>Customer</b></p></div><div class='span1'><p style='text-align: center'><b>Error</b></p></div><div class='span1'><p style='text-align: center'><b>Ngrams</b></p></div><div class='span1'><p class='pull-left' style='text-align: center'><b>Noun Pharses</b></p></div></fieldset>")
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


App.ReviewsCountParentView = Backbone.View.extend({
	template: window.template("reviews-count-parent"),
	tagName: "table",
	className: "table count-table",
	initialize: function(options){
		this.model = options.model;
		this.data = this.model.data;
	},

	render: function(){
		var self = this;
		this.$el.append(this.template(this));
		$.each(self.data, function(iter, city_dict){
			var subView = new App.ReviewsCountChildView({model: {"city": city_dict.city, "classified": city_dict.classified, "unclassified": city_dict.unclassified}});

			self.$("#reviewsCount").append(subView.render().el);	
		});
		this.afterRender();
		return this;
	},

	afterRender: function(){
		},


})	

App.ReviewsCountChildView = Backbone.View.extend({
	template: window.template("reviews-count-child"),
	tagName: "tr",
	city: function(){return this.model.city}, 
	classified: function(){return this.model.classified}, 
	unclassified: function(){return this.model.unclassified}, 

	initialize: function(options){
		this.model = options.model;
	},

	render: function(){
		this.$el.append(this.template(this));
		return this;
	},
	
});



App.ClassfiedReviewsView = Backbone.View.extend({
	template: window.template("classified-reviews"),
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
	template: window.template("unclassified-reviews"),
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
	template: window.template("each-eatery"),
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
	template: window.template("root-top"),

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



App.NgramsParent = Backbone.View.extend({
	tagName: "fieldset",
	className: "well plan-name",
	template: window.template("ngrams-parent"),
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
	
	template: window.template("ngram"),
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



});



