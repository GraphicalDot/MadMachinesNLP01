$(document).ready(function(){

App = {} ;
window.App = App ;
window.template = function(name){ return Mustache.compile($("#"+name+"-template").html()); };
preloaderString = '<div class="progress" ><div class="indeterminate"></div></div>'




App.BodyView = Backbone.View.extend({

	initialize: function(){
		var self = this;
		$(".submitText").click(function(){
			$("body .container").append(preloaderString)
			text = $("#textarea").val()

			var jqhr = $.post("http://localhost:8000/sentence_tokenization", {"text": text, "link": null})

			jqhr.done(function(data){
				$(".progress").remove();
				if (data.error == false){

					$("#sentences").html("")
					$("#sentences").append('<ul class="collection" id="sentenceCollection"></ul>')
					$.each(data.result, function(iter, setenceObject){
						var subView = new App.SentencesView({"model": setenceObject})
					 	$("#sentenceCollection").append(subView.render().el);

					});
					$('select.tags').material_select();
					$('select.polarity').material_select();
				}
				else{
					console.log("error occireed")

				}

			})

		})


		$('.modal-trigger').leanModal({
				dismissible: true, // Modal can be dismissed by clicking outside of the modal
		      		opacity: .5, // Opacity of modal background
				in_duration: 300, // Transition in duration
				out_duration: 200, // Transition out duration
				complete: function() {
					var __value = $("#textarealink").val()
					$("body .container").append(preloaderString)

					var jqhr = $.post("http://localhost:8000/sentence_tokenization", {"text": null, "link": __value})

					jqhr.done(function(data){
						$(".progress").remove();
						if (data.error == false){
							$("#sentences").html("")
							$("#sentences").append('<ul class="collection" id="sentenceCollection"></ul>')
							$.each(data.result, function(iter, setenceObject){
								var subView = new App.SentencesView({"model": setenceObject})
					 			$("#sentenceCollection").append(subView.render().el);

							})
						}
						else{
							console.log("error occireed")

							}

						})
				}
					});


		$('select').material_select();
		},




	render: function(){
		$('#token_select').material_select();
		return this;
	},

});


App.SentencesView = Backbone.View.extend({
		tagName: "li",
		// className: "collection-item card-panel #ffe0b2 orange lighten-4 z-depth-3",
		className: "row white hoverable sentences_row_inside",
		template: window.template("sentences"),
		sentence: function(){ return this.model.sentence},
		mixed: function(){return this.model.sentiment_probabilities.mixed},
		positive: function(){return this.model.sentiment_probabilities.positive},
		negative: function(){return this.model.sentiment_probabilities.negative},
		neutral: function(){return this.model.sentiment_probabilities.neutral},
		polarity_result: function(){return this.model.polarity_result},
		tree: function(){return  "data:image/jpg;base64," + this.model.encoded_string},
		noun: function() {return this.model.tb_conll_nps.join(",")},
		noun2: function() {return this.model.te_nps.join(",")},

		initialize: function(options){
			this.model = options.model;

		},

		render:  function(){
			this.$el.append(this.template(this));

			this.$(".tags").val(this.model.tag);
			this.$(".polarity").val(this.model.polarity);
			this.$(".subTags").val(this.model.subcategory);
			this.changeOptions(this.model.tag);
			this.$el.attr("style", "color: black ");
			var self= this;
			setTimeout(function() {
				makeData(self.$el.find('svg')[0], self.model.sentence, self.model.dependencies);
			}, 0);
			return this;

		},


		changeOptions: function(tag){

			foodsubtags = ['dishes', 'menu-food', 'null-food', 'overall-food', 'place-food', 'sub-food'];
			costsubtags = ['cheap', 'cost-null', 'expensive', 'not worth', 'value for money'];
			servicesubtags = ['booking', 'management', 'presentation', 'service-null', 'service-overall', 'staff', 'waiting-hours'];
			ambiencesubtags = ['ambience-null', 'ambience-overall', 'crowd', 'dancefloor', 'decor', 'in-seating', 'music', 'open-area', 'romantic', 'smoking-zone', 'sports', 'sports-screens', 'view', 'sports-props'];
			overall = [];

			var self = this;
			if (tag == "food"){
				$.each(foodsubtags, function(iter, subTag){
					var __str = "<option value='" + subTag + "'>" + subTag  + "</option>" ;
					self.$("select.subTags").append(__str);

			})};
			if (tag == "cost"){
				$.each(costsubtags, function(iter, subTag){
					var __str = "<option value='" + subTag + "'>" + subTag  + "</option>" ;
					self.$("select.subTags").append(__str);

			})};
			if (tag == "ambience"){
				$.each(ambiencesubtags, function(iter, subTag){
					console.log(subTag);
					var __str = "<option value='" + subTag + "'>" + subTag  + "</option>" ;
					self.$("select.subTags").append(__str);

			})};
			if (tag == "service"){
				$.each(servicesubtags, function(iter, subTag){
					console.log(subTag);
					var __str = "<option value='" + subTag + "'>" + subTag  + "</option>" ;
					self.$("select.subTags").append(__str);

			})};

			self.$("select.subTags").material_select();


		},


		events: {
			"click .sendButton": "sendButton",
			"change .tags": "changeTag"
		},


		changeTag: function(event){
			event.preventDefault();
			event.stopPropagation();
			var x= $(this.el).find('select.tags').val();
			this.$(".subTags").html("");
			this.$(".subTags").append("<select class='subTags'></select>");
			this.changeOptions(x);


		},
		sendButton: function(event){
			var self = this;
			event.preventDefault();
			console.log("send button clicked");
			console.log(this.model.sentence)
			var jqhr = $.post("http://localhost:8000/upload_sentence", {"sentence": this.model.sentence, "sentiment": self.$(".polarity").val(), "tag": self.$(".tags").val(), "subtag": self.$(".subTags").val()} )
			jqhr.done(function(data){
				console.log(data)
				if (data.success == true){
						 Materialize.toast('SEntence has been uploaded', 4000)
				}
				else{
					 Materialize.toast('Someproblem occurred, While processing your request', 4000)
				}

			})
			this.remove();
		}


})






});
