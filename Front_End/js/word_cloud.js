$(document).ready(function(){
/*

App.SeeWordCloudDateSelectionView = Backbone.View.extend({
	template: window.template("bubbles-svg"),
	initialize: function(options){
		this.$el.append(this.template(this));
		this.beforeRender();	
	},

	render: function(){
		return this;	
	},

	beforeRender: function(){
		console.log(this.el)
		var data = [4, 8, 15, 16, 23, 42];

		var width = 420,
		barHeight = 20;

		var x = d3.scale.linear()
			.domain([0, d3.max(data)])
			.range([0, width]);

		var chart = d3.select(this.$(".chart"))
			.attr("width", width)
			.attr("height", barHeight * data.length);

		var bar = chart.selectAll("g")
	    .data(data)
	      .enter().append("g")
	          .attr("transform", function(d, i) { return "translate(0," + i * barHeight + ")"; });

bar.append("rect")
	    .attr("width", x)
	        .attr("height", barHeight - 1);

bar.append("text")
	    .attr("x", function(d) { return x(d) - 3; })
	        .attr("y", barHeight / 2)
		    .attr("dy", ".35em")
		        .text(function(d) { return d; });



		$("body").append('<div><svg width="720" height="120"><circle cx="40" cy="60" r="10"></circle><circle cx="80" cy="60" r="10"></circle><circle cx="120" cy="60" r="10"></circle><circle cx="120" cy="60" r="10"></circle><circle cx="160" cy="60" r="10"></circle><circle cx="200" cy="60" r="10"></circle></svg></div>')

		
		var svg = d3.select("svg");
		var circle = svg.selectAll("circle")
			.data([32, 57, 200, 293], function(d) { return d; });

		circle.enter().append("circle")
			.attr("cy", 60)
			.attr("cx", function(d, i) { return i * 100 + 30; })
			.attr("r", function(d) { return Math.sqrt(d); });
		
		circle.exit().remove();
		d3.select("body").selectAll("circle").transition()
	    .duration(750)
	    .delay(function(d, i) { return i * 10; })
	    .attr("r", function(d) { return Math.sqrt(d * scale); });
		console.log("Something happened")
	}, 


});
*/

App.SeeWordCloudDateSelectionView = Backbone.View.extend({
	template: window.template("see-word-cloud-date-selection"),
	tag: "form",
	className: "form-horizontal",
	initialize: function(options){
	},

	render: function(){
		this.beforeRender();	
		this.$el.append(this.template(this));
		return this;	
	},

	beforeRender: function(){
		var self = this;
		var jqhr = $.post(window.get_start_date_for_restaurant, {"eatery_id": $("#eateriesList").find('option:selected').attr("id")})	
		jqhr.done(function(data){
			console.log(data.result)
			self.$("#startDate").val(data.result.start)
			self.$("#selectStartDate").val(data.result.start)
			self.$("#endDate").val(data.result.end)
			self.$("#selectEndDate").val(data.result.end)
		});


	}, 

	events: {
		"click #idSubmit": "submit",
		"click #idCancel": "cancel",

	},

	submit: function(event){
		var self = this;
		$(".dynamic_display_word_cloud").empty();	
		event.preventDefault();
		this.$el.addClass("dvLoading");
		if ($('#startDate').val() > $('#selectStartDate').val()){
			bootbox.alert("Genius the start date selected should be greater then start date").find('.modal-content').addClass("bootbox-modal-custom-class");
			return

		}
		if ($('#endDate').val() < $('#selectEndDate').val()){

			bootbox.alert("Genius the end date selected should be less then end date").find('.modal-content').addClass("bootbox-modal-custom-class");
			return
		}
	
	
		var jqhr = $.post(window.get_word_cloud, {"eatery_id": $("#eateriesList").find('option:selected').attr("id"),
							"start_date": $('#selectStartDate').val(),
							"end_date": $('#selectEndDate').val(),
		    					"category": $("#wordCloudCategory").find("option:selected").val(),
						})	
		jqhr.done(function(data){
			$.each(data.result, function(iter, noun_phrase_dict){
				var subView = new App.SeeWordCloudDateMainView({model: noun_phrase_dict});
				$(".dynamic_display_word_cloud").append(subView.render().el);	
				$(".dynamic_display_word_cloud").append('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');	
			});
			self.$el.removeClass("dvLoading");
		
			});
		jqhr.fail(function(){
				bootbox.alert("Either the api or internet connection is not working, Try again later")
				self.$el.removeClass("dvLoading");
				event.stopPropagation();
		});

	
	},





	cancel: function(event){
		event.preventDefault();
		this.remove();
	},

});

App.SeeWordCloudDateMainView = Backbone.View.extend({
	template: Mustache.compile('{{nounPhrase}}'),
	tagName: "a",
	size: function(){return this.model.frequency*10},
	nounPhrase: function(){return this.model.name},
	polarity: function(){return this.model.polarity},
	

	initialize: function(options){
		this.model = options.model;
		console.log(this.size())
		console.log(this.polarity())
		
	},

	render: function(){
		this.$el.append(this.template(this));
		this.afterRender();
		return this;
	},

	afterRender: function(){
		var self = this;
		this.$el.attr({href: "#", rel: this.size()});
		this.$el.css({"font-size": this.size()})
		if(self.polarity() == "negative"){
			console.log(" Negative polkrariy aaying");	
			self.$el.css({"color": "red"})
		}
	},

});
});
