
$(document).ready(function(){
window.data = [{'polarity': 'negative', 'frequency': 1, 'name': 'paneer steak'},
{'polarity': 'positive', 'frequency': 1, 'name': 'conti dish'}, {'polarity': 'positive', 'frequency': 1, 'name': 'glad i'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'bank cards'}, {'polarity': 'positive', 'frequency': 1, 'name': 'pizza didn'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'cottage cheese steak'}, {'polarity': 'negative', 'frequency': 1, 'name': 'chicken veloute soup'}
, {'polarity': 'negative', 'frequency': 1, 'name': 'flavour ...'}, {'polarity': 'positive', 'frequency': 1, 'name': 'vegan teetotaller orders'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'italian steak'}, {'polarity': 'positive', 'frequency': 1, 'name': 'peaceful date'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'anyways'}, {'polarity': 'negative', 'frequency': 1, 'name': 'right amount'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'superb'}, {'polarity': 'negative', 'frequency': 1, 'name': 'watermelon base'}, 
{'polarity': 'positive', 'frequency': 2, 'name': 'paneer shashlik'}, {'polarity': 'positive', 'frequency': 1, 'name': 'great cafe'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'cheese steak burger'}, {'polarity': 'positive', 'frequency': 1, 'name': '.25 minutes'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'n high seats'}, {'polarity': 'positive', 'frequency': 1, 'name': 'new favorite place'}, 
{'polarity': 'negative', 'frequency': 1, 'name': 'expensive place'}, {'polarity': 'positive', 'frequency': 1, 'name': 'spread'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'veg quesadillas'}, {'polarity': 'positive', 'frequency': 1, 'name': '% discount'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'recommended'}, {'polarity': 'positive', 'frequency': 1, 'name': 'italian cheese steak burger'}, 
{'polarity': 'negative', 'frequency': 1, 'name': '..sister concern'}, {'polarity': 'positive', 'frequency': 1, 'name': 'pleasant surprise'}, 
{'polarity': 'negative', 'frequency': 1, 'name': 'crisp corn'}, {'polarity': 'positive', 'frequency': 1, 'name': 'bucks + taxes'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'town house caf\xe9'}, {'polarity': 'positive', 'frequency': 1, 'name': 'great place'}, 
{'polarity': 'negative', 'frequency': 1, 'name': 'deep flavor'}, {'polarity': 'positive', 'frequency': 1, 'name': 'server joins'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'food lovers'}, {'polarity': 'negative', 'frequency': 1, 'name': 'paneer shashlik'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'good company'}, {'polarity': 'positive', 'frequency': 1, 'name': 'wow'}, 
{'polarity': 'negative', 'frequency': 1, 'name': 'wall units'}, {'polarity': 'positive', 'frequency': 1, 'name': 'unique dish'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'pure vegetarian'}, {'polarity': 'positive', 'frequency': 1, 'name': 'suggestion'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'dark chocolate mouse needless'}, {'polarity': 'negative', 'frequency': 1, 'name': 'red lamps'}, 
{'polarity': 'negative', 'frequency': 1, 'name': 'margarita pizza'}, {'polarity': 'positive', 'frequency': 1, 'name': 'tender meat'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'n g'}, {'polarity': 'positive', 'frequency': 1, 'name': 'bhutte ke kebab'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'hummus pita'}, {'polarity': 'negative', 'frequency': 1, 'name': 'real gem'}, 
{'polarity': 'positive', 'frequency': 2, 'name': 'inr'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'good servicegood ambiencetasty foodnice staffi'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'good food'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'bell pepper'}, {'polarity': 'positive', 'frequency': 1, 'name': 'red pasta'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'great main course'}, {'polarity': 'positive', 'frequency': 1, 'name': 'pasta good'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'mortedela'}, {'polarity': 'positive', 'frequency': 1, 'name': 'good burger'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'delhi ncr'}, {'polarity': 'positive', 'frequency': 2, 'name': 'hookah'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'old techno tracks'}, {'polarity': 'positive', 'frequency': 1, 'name': 'connaught'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'couch'}, {'polarity': 'positive', 'frequency': 1, 'name': 'long time'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'tough leathery slice'}, {'polarity': 'positive', 'frequency': 1, 'name': 'melt burger'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'college friend\u2019s'}, {'polarity': 'positive', 'frequency': 1, 'name': 'it\u2019s'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'main part'}, {'polarity': 'positive', 'frequency': 1, 'name': 'perfect'}, 
{'polarity': 'negative', 'frequency': 1, 'name': 'penny arabiatta'}, {'polarity': 'negative', 'frequency': 1, 'name': 'brain freezer'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'axis'}, {'polarity': 'positive', 'frequency': 1, 'name': 'non veg'}, 
{'polarity': 'positive', 'frequency': 2, 'name': 'nice place'}, {'polarity': 'positive', 'frequency': 1, 'name': 'available..a mixture'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'red lemonade'}, {'polarity': 'negative', 'frequency': 1, 'name': 'terrible time'}, 
{'polarity': 'negative', 'frequency': 1, 'name': 'place u'}, {'polarity': 'negative', 'frequency': 1, 'name': 'warehouse cafe ...'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'paneer steak'}, {'polarity': 'positive', 'frequency': 1, 'name': 'juicy burger'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'classic greek salad'}, {'polarity': 'negative', 'frequency': 1, 'name': 'ordinary stuff'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'satisfactory nd'}, {'polarity': 'positive', 'frequency': 1, 'name': 'perfect place'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'overall gud'}, {'polarity': 'positive', 'frequency': 1, 'name': 'huge acreage'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'chilli paneer'}, {'polarity': 'positive', 'frequency': 1, 'name': 'chinese dish'}, 
{'polarity': 'negative', 'frequency': 1, 'name': '... ..'}, {'polarity': 'positive', 'frequency': 1, 'name': 'fresh bun'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'different types'}, {'polarity': 'positive', 'frequency': 1, 'name': 'chilli potatoes'}, 
{'polarity': 'negative', 'frequency': 1, 'name': 'jazzy lit'}, {'polarity': 'positive', 'frequency': 1, 'name': 'culinary experience'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'thai'}, {'polarity': 'positive', 'frequency': 1, 'name': 'ground floor'}, 
{'polarity': 'positive', 'frequency': 1, 'name': 'juicy patty'}, {'polarity': 'positive', 'frequency': 1, 'name': 'loved'}]

App.RootView = Backbone.View.extend({
	initialize: function(options){
	
		this.model = options.model
		console.log("Root view called")
		console.log(this.model.el)
		this.__d3_circular_word_cloud();
		//this.__d3_simple_cloud();
	},

	render: function(){
		return this;
	},
	
	events: {
		},
	
	__d3_simple_cloud: function(){
		d3.select(this.el).selectAll("p")
				.data(window.data)
				.enter()
				.append("b")
				.text(function(d){ return d.name;})
				.style("color", function(d) {
					if(d.polarity == "negative"){   //Threshold of 15
						return "red";
					}
					else{
						return "black";
					}
				})
				.style("font-size", function(d){
					return d.frequency*30
				})
				.style("width", "400px")
				.style("margin-top",  function(d){
					return 1000*d.frequency + "px"})
				.style("margin-right",  function(d){
					return 50*d.frequency + "px"})
				.style("margin-bottom",  function(d){
					return 1000*d.frequency + "px"})
				.style("margin-left",  function(d){
					return 50*d.frequency + "px"})

	},
	__d3_circular_word_cloud: function(){
		console.log("__d3 called")
		var w = 500;
		var h = 50;

		d3.select(this.el).append("svg")
			.attr("width", 200)
			.attr("height", 200)
			.selectAll("circle")
		/*
			.data(window.data)
			.enter()
			.append("circle")
			.attr("cx", function(d, i) {
			            return (i * 50) + 25;
				            })
			.attr("cy", h/2)
			.attr("r", function(d) {
				return d.frequency;
							         });
			*/
	},

});
});


