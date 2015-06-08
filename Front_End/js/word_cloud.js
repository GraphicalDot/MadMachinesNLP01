$(document).ready(function(){



App.SeeWordCloudDateSelectionView = Backbone.View.extend({
	template: window.template("see-word-cloud-date-selection"),
	tag: "form",
	className: "form-horizontal",
	initialize: function(options){
		function newfunction(){
			function another(){
				console.log(this)
			}
			another()
		}
		console.log(this)
		newfunction()
	},


	render: function(){
		this.beforeRender();
		this.$el.append(this.template(this));
		return this;	
	},

	beforeRender: function(){
		var self = this;
		window.eatery_id = $(":checkbox:checked").attr("id");
	
		/*	
		var jqhr = $.post(window.get_start_date_for_restaurant, {"eatery_id": window.eatery_id})	
		jqhr.done(function(data){
			console.log(data.result)
			self.$("#startDate").val(data.result.start)
			self.$("#selectStartDate").val(data.result.start)
			self.$("#endDate").val(data.result.end)
			self.$("#selectEndDate").val(data.result.end)
		});
		*/
		},


	events: {
		"click #idSubmit": "submit",
		"click #idCancel": "cancel",

	},

	loading_bootbox: function(){
		$(".data_selection").modal("hide");
		bootbox.dialog({ 
			closeButton: false, 
			message: "<img src='css/images/loading.png'>",
			className: "loadingclass",
		});
	},

	submit: function(event){
		var self = this;
		$(".dynamic_display_word_cloud").empty();	
		event.preventDefault();
		this.$el.addClass("dvLoading");
	
		window.word_cloud_category =  $("#wordCloudCategory").find("option:selected").val();

		console.log("This is the category selected" + window.word_cloud_category);	
		/*
		if (window.word_cloud_category == "Service"){
			bootbox.alert("The service word cloud has not been implemented yet !!");
			$(".loadingclass").modal("hide");
			$(".data_selection").modal("hide");
			$.each($(":checkbox"), function(iter, __checkbox){
				$("#" + __checkbox.id).prop("checked", false); 
				})
			return 
		}

		*/
		this.loading_bootbox()
		/*
		if ($('#startDate').val() > $('#selectStartDate').val()){
			bootbox.alert("Genius the start date selected should be greater then start date").find('.modal-content').addClass("bootbox-modal-custom-class");
			return

		}
		if ($('#endDate').val() < $('#selectEndDate').val()){

			bootbox.alert("Genius the end date selected should be less then end date").find('.modal-content').addClass("bootbox-modal-custom-class");
			return
		}
	
		*/
		//payload = {"eatery_id": eatery_id, "category":"overall", "total_noun_phrases": 15, "word_tokenization_algorithm": 
		//	'punkt_n_treebank', "pos_tagging_algorithm": "hunpos_pos_tagger", "noun_phrases_algorithm":"regex_textblob_conll_np"}
		


		console.log(window.eatery_id + "    " + window.word_cloud_category);	
		var jqhr = $.post(window.get_word_cloud, {"eatery_id": window.eatery_id,
		//					"start_date": $('#selectStartDate').val(),
		//					"end_date": $('#selectEndDate').val(),
		    					"category": window.word_cloud_category,
							"total_noun_phrases": 20,	
					})


		
		//On success of the jquery post request
		jqhr.done(function(data){
			var subView = new App.WordCloudWith_D3({model: data.result});
			$(".loadingclass").modal("hide");
			

			$.each(data.sentences, function(iter, sentence){
				var subView = new App.RootRowView({model: sentence}); 
				$(".sentences").append(subView.render().el)
			})
			});

		//In case the jquery post request fails
		jqhr.fail(function(data){
				bootbox.alert(data.messege)
				self.$el.removeClass("dvLoading");
				event.stopPropagation();
		});

	
	},





	cancel: function(event){
		event.preventDefault();
		$(".data_selection").modal("hide");
		$.each($(":checkbox"), function(iter, __checkbox){
				$("#" + __checkbox.id).prop("checked", false); 
	})
	},

});


App.WordCloudWith_D3 = Backbone.View.extend({
	initialize: function(options){
		//In case svg was present on the page
		d3.select("svg").remove()
		this.model = options.model
		console.log(this.model)
		this._data = options.model
		//this.ChangingBarLayout(this.model);
		this.BarLayout(this.model);
		//this.ForceLayout(this.model);
		},
	

	dataFunction: function(value, LEVEL){

		function ADD_EX_BUBBLES(old_array){
			for(var i = 0; i < window.EX_BUBBLES; i++){
				old_array.push({"name": "NULL", 
						"polarity": 2, 
						"r": .1,})
			}
				    return old_array;
		}


		function if_data_empty(a_rray){
			if(a_rray == undefined){
				LEVEL = LEVEL -1
				bootbox.alert("There is no after level for this tag")
			}
		
			return true
		}
		
		var newDataSet = [];
		if (LEVEL == 0){
			$.each(this._data, function(i, __d){
				newDataSet.push({"name": __d.name, 
						"ptime": __d.ptime, 
						"positive": __d.positive,
						"negative": __d.negative,
						"neutral": __d.neutral,
						"sentences": __d.sentences,
						"similar": __d.similar,
						"superpositive": __d.superpositive,
						"supernegative": __d.supernegative,
						"r": __d.positive+__d.negative + __d.neutral + __d.supernegative + __d.superpositive,
						}); }); return newDataSet }
			
		if(LEVEL == 1){
			PARENT_LEVEL_1 = value
			$.each(this._data, function(i, __d){
				if (__d.name == value){
					$.each(__d.children, function(i, _d){
						newDataSet.push({"name": _d.name, 
							"polarity": _d.polarity, 
							"r": _d.frequency,
							}); }); }; }); return newDataSet}
		if(LEVEL == 2){ 
			PARENT_LEVEL_2 = value
			$.each(this._data, function(i, __d){
				if (__d.name == PARENT_LEVEL_1){
					$.each(__d.children, function(i, _d){
						if (_d.name == PARENT_LEVEL_2){
							if_data_empty(_d.children)
							$.each(_d.children, function(i, child){
								newDataSet.push({"name": child.name, 
									"polarity": child.polarity, 
									"r": child.frequency,
									}); }); }; }); }; }); return newDataSet}
		
		if(LEVEL == 3){ 
			PARENT_LEVEL_3 = value
			$.each(this._data, function(i, __d){
				if (__d.name == PARENT_LEVEL_1){
					$.each(__d.children, function(i, _d){
						if (_d.name == PARENT_LEVEL_2){
							$.each(_d.children, function(i, child){
								if (child.name == PARENT_LEVEL_3){
									if_data_empty(child.children)
									$.each(child.children, function(i, __child){
										newDataSet.push({"name": __child.name, 
										"polarity": __child.polarity, 
										"r": __child.frequency,
								}); }); }; }); }; }); }; }); return newDataSet}
		},

	ChangingBarLayout: function(_data){
		/* 
		 * http://bl.ocks.org/mbostock/1134768
		 [[u'vada pao bao', u'neutral', u'2015-01-07 13:23:45'],
 		[u'chilli paneer', u'neutral', u'2015-01-07 13:23:45'],
		[u'mezze platter', u'neutral', u'2015-01-07 13:23:45'],
		[u'chicken burger', u'neutral', u'2015-01-07 17:10:56'],
		[u'china box', u'neutral', u'2015-01-07 18:32:04'],
		[u'vada pao bao', u'negative', u'2015-01-07 18:32:04'],
		[u'china box', u'super-positive', u'2015-01-07 23:37:34'],
		[u'chicken wings', u'super-positive', u'2015-01-08 13:57:09'],
		[u'mezze platter', u'super-positive', u'2015-01-08 13:57:09'],
		[u'oreo mud pot', u'super-positive', u'2015-01-08 13:57:09'],
		[u'vada pao bao', u'positive', u'2015-01-08 23:23:55'],
		[u'keema pao', u'super-positive', u'2015-01-08 23:23:55'],
		[u'pepper china box', u'super-positive', u'2015-01-08 23:23:55']] 
		 */


		

		noun_phrases = _data.noun_phrases;
		var noun_phrases = [ {'name': 'strawberry cheesecake', 'ptime': '2014-08-12 22:12:34', 'positive': 1, 'negative': 0, 
			'supernegative': 0, 'neutral': 0, 'superpositive': 0}, 
			     {'name': 'strawberry cheesecake', 'ptime': '2014-08-11 18:51:39', 'positive': 0, 'negative': 0, 
				     'supernegative': 0, 'neutral': 1, 'superpositive': 0}, 
			     {'name': 'strawberry cheesecake', 'ptime': '2014-08-03 18:01:10', 'positive': 1, 'negative': 0, 
				     'supernegative': 0, 'neutral': 0, 'superpositive': 0}, 
			     {'name': 'strawberry cheesecake', 'ptime': '2014-08-01 21:51:03', 'positive': 0, 'negative': 0, 
				     'supernegative': 0, 'neutral': 1, 'superpositive': 0}, 
			     {'name': 'strawberry cheesecake', 'ptime': '2014-11-21 12:01:09', 'positive': 0, 'negative': 0, 
				     'supernegative': 0, 'neutral': 1, 'superpositive': 0}, 
			     {'name': 'loaded nachos', 'ptime': '2014-08-23 00:48:53', 'positive': 1, 'negative': 0, 
				     'supernegative': 0, 'neutral': 0, 'superpositive': 0}, 
			     {'name': 'loaded nachos', 'ptime': '2014-08-01 21:51:03', 'positive': 1, 'negative': 0, 
				     'supernegative': 0, 'neutral': 0, 'superpositive': 0}, 
			     {'name': 'loaded nachos', 'ptime': '2014-12-09 00:20:36', 'positive': 1, 'negative': 0, 
				     'supernegative': 0, 'neutral': 0, 'superpositive': 0}, 
			     {'name': 'loaded nachos', 'ptime': '2014-10-06 14:06:25', 'positive': 1, 'negative': 0, 
				     'supernegative': 0, 'neutral': 0, 'superpositive': 0}, 
			     {'name': 'loaded nachos', 'ptime': '2014-09-25 11:01:33', 'positive': 1, 'negative': 0, 
				     'supernegative': 0, 'neutral': 0, 'superpositive': 0}, 
			     {'name': 'loaded nachos', 'ptime': '2014-09-26 15:49:53', 'positive': 0, 'negative': 0, 
				     'supernegative': 0, 'neutral': 1, 'superpositive': 0}, 
			     {'name': 'deconstructed moscow mule', 'ptime': '2014-08-23 00:48:53', 'positive': 1, 'negative': 0, 
				     'supernegative': 0, 'neutral': 0, 'superpositive': 0}, 
			     {'name': 'deconstructed moscow mule', 'ptime': '2014-11-02 12:24:41', 'positive': 0, 'negative': 0, 
				     'supernegative': 0, 'neutral': 1, 'superpositive': 0}]

		
		
		keys = _data.keys;
		var keys = [{'name': 'strawberry cheesecake'}, {'name': 'deconstructed moscow mule'}, {'name': 'loaded nachos'}]
		
		console.log(keys)
		_this = this;
		/*
		function DATA(value, LEVEL){return  _this.dataFunction(value, LEVEL)}
		LEVEL = 0
		
		data = DATA(null, LEVEL);
		*/
		var RScale = d3.scale.linear()
			 	.range([0, width-200])
				//.domain([0, d3.max(keys, function(d) { return d.r; })])
				.domain([0, 10])
		var width = $(window).width() - $(".append_eatery").width()*1.5;
		var height = $(window).height();
		var barHeight = 25;

		var transitionTime = 50;
		var svg = d3.select(".main-body").append("svg")
			.attr("width", width)
			.attr("height", height*1.5)
			.style("shape-rendering", "crispEdges")	
			.style("margin-top", height/15)	



			
		$.each(noun_phrases, function(iter, key){
			update(key)	
		})

		function update(__key){
			var bar = svg.selectAll("g")
				.data(keys, function(d, i){return d.name})
			        
			bar.enter().append("g")
				.attr("class",function(d) { return d.name })
			bar.exit().remove();
			
			
			rects = bar.selectAll("rect")
				.data(function(d){return d.name})

			rects.enter().append("rect")
				.style("fill", "green") 
				.attr("width", function(d) {return 10})
				.transition().delay(function (d,i){ return i * transitionTime;}).duration(transitionTime)	
		  		.attr("height", barHeight);
			
			/*	
			bar
				.append("rect")
				.attr("class", "dishes")
				.style("fill", "green") 
				.attr("width", function(d) {return RScale(d.superpositive); })
				.transition().delay(function (d,i){ return i * transitionTime;}).duration(transitionTime)	
		  		.attr("height", barHeight - 1);
		
			bar
				.append("rect")
				.style("fill", "yellowgreen") 
				.attr("width", function(d) {return RScale(d.positive); })
				.transition().delay(function (d,i){ return i * transitionTime;}).duration(transitionTime)	
				.attr("height", barHeight - 1)
				.attr("transform", function(d, i) { return "translate(" + RScale(d.superpositive) +", 0)"; });
			
			bar
				.append("rect")
				.style("fill", "PaleTurquoise") 
				.attr("width", function(d) {return RScale(d.neutral); })
				.transition().delay(function (d,i){ return i * transitionTime;}).duration(transitionTime)	
				.attr("height", barHeight - 1)
				.attr("transform", function(d, i) { return "translate(" + RScale(d.superpositive+d.positive) +", 0)"; });
		
			bar
				.append("rect")
				.style("fill", "lightpink") 
				.attr("width", function(d) { console.log(RScale(d.r)); return RScale(d.negative); })
				.transition().delay(function (d,i){ return i * transitionTime;}).duration(transitionTime)	
				      .attr("height", barHeight - 1)
				.attr("transform", function(d, i) { return "translate(" + RScale(d.superpositive+d.positive+d.neutral) +", 0)"; });
		
		
			bar
				.append("rect")
				.style("fill", "red") 
				.attr("width", function(d) { console.log(RScale(d.r)); return RScale(d.supernegative); })
				.transition().delay(function (d,i){ return i * transitionTime;}).duration(transitionTime)	
				.attr("height", barHeight - 1)
				.attr("transform", function(d, i) { return "translate(" + RScale(d.superpositive+d.positive+d.neutral+d.negative) +", 0)"; });
			bar.append("text")
				.transition().delay(function (d,i){ return i * transitionTime;}).duration(transitionTime)
				.attr("x", function(d) { return RScale(d.r) + 4; })
				.attr("y", barHeight / 2)
				.attr("dy", ".35em")
				.text(function(d) { return d.name; })
				.style("font-size", function(d){return barHeight/2 + "px"})
				.style("font-family", "'Source Sans Pro', sans-serif")
			*/
				}
		//drawNodes(data())
	},

	BarLayout: function(_data){
		/* 
		 * http://bl.ocks.org/mbostock/1134768
		 
		 {u'name': u'strawberry cheesecake', u'negative': 0, 'supernegative': 0, u'neutral': 4, 
		 u'timeline': [[u'super-positive', u'2014-08-19 09:11:52'], [u'neutral', u'2014-09-29 14:17:48'], 
		 [u'positive', u'2014-08-12 22:12:34'], [u'neutral', u'2014-08-11 18:51:39'], [u'positive', u'2014-08-03 18:01:10'], 
		 [u'neutral', u'2014-08-01 21:51:03'], [u'neutral', u'2014-11-21 12:01:09']], 'superpositive': 1, 
		 u'similar': [u'strawberry cheese cake', u'strawberry cheesecake'], u'positive': 2}, 
		 
		 {u'name': u'loaded nachos', u'positive': 5, u'negative': 0, 'supernegative': 0, u'neutral': 1, u'timeline': 
		 [[u'positive', u'2014-08-23 00:48:53'], [u'positive', u'2014-08-01 21:51:03'], [u'positive', u'2014-12-09 00:20:36'], 
		 [u'positive', u'2014-10-06 14:06:25'], [u'positive', u'2014-09-25 11:01:33'], [u'neutral', u'2014-09-26 15:49:53']], 
		 'superpositive': 0, u'similar': []}, {u'name': u'deconstructed moscow mule', u'positive': 3, u'negative': 0, 
		 'supernegative': 0, u'neutral': 1, u'timeline': [[u'positive', u'2014-08-23 00:48:53'], 
		 [u'super-positive', u'2014-08-20 21:06:16'], [u'positive', u'2014-07-21 16:45:36'], 
		 [u'super-positive', u'2014-12-10 12:18:05'], [u'positive', u'2014-12-14 14:10:19'], [u'neutral', u'2014-11-02 12:24:41']], 
		 'superpositive': 2, 
		 u'similar': []}]
		  Now get have started executing 
		 */

		_this = this;
		function DATA(value, LEVEL){return  _this.dataFunction(value, LEVEL)}
		LEVEL = 0
		var width = $(window).width() - $(".append_eatery").width()*1.5;
		var height = $(window).height();
		var barHeight = 25;

		data = DATA(null, LEVEL);


		var transitionTime = 300;
		var RScale = d3.scale.linear()
			 	.range([0, width-200])
				.domain([0, d3.max(data, function(d) { return d.r; })])
		
		var svg = d3.select(".main-body").append("svg")
			.attr("width", width)
			.attr("height", height*1.5)
			.style("shape-rendering", "crispEdges")	
			.style("margin-top", height/15)	

		var bar = svg.selectAll("g")
				.data(DATA(null, LEVEL))
			        .enter().append("g")
				//.style("stroke", function(d, i) { return d3.rgb(i).darker(); })
				.attr("id", function(d, i) { return d.name})
				.attr("transform", function(d, i) { return "translate(0," + i * barHeight + ")"; })
		

		bar
				.append("rect")
				.attr("class", "dishes")
				.style("fill", "green") 
				.attr("width", function(d) {return RScale(d.superpositive); })
				.transition().delay(function (d,i){ return i * transitionTime;}).duration(transitionTime)	
		  		.attr("height", barHeight - 1);
		
		bar
				.append("rect")
			.style("fill", "yellowgreen") 
			.attr("width", function(d) {return RScale(d.positive); })
				.transition().delay(function (d,i){ return i * transitionTime;}).duration(transitionTime)	
				      .attr("height", barHeight - 1)
			.attr("transform", function(d, i) { return "translate(" + RScale(d.superpositive) +", 0)"; });
		bar
				.append("rect")
			.style("fill", "PaleTurquoise") 
			.attr("width", function(d) {return RScale(d.neutral); })
				.transition().delay(function (d,i){ return i * transitionTime;}).duration(transitionTime)	
				      .attr("height", barHeight - 1)
		
			.attr("transform", function(d, i) { return "translate(" + RScale(d.superpositive+d.positive) +", 0)"; });
		bar
				.append("rect")
			.style("fill", "lightpink") 
			.attr("width", function(d) { console.log(RScale(d.r)); return RScale(d.negative); })
				.transition().delay(function (d,i){ return i * transitionTime;}).duration(transitionTime)	
				      .attr("height", barHeight - 1)
			.attr("transform", function(d, i) { return "translate(" + RScale(d.superpositive+d.positive+d.neutral) +", 0)"; });
		
		
		bar
				.append("rect")
			.style("fill", "red") 
			.attr("width", function(d) { console.log(RScale(d.r)); return RScale(d.supernegative); })
				.transition().delay(function (d,i){ return i * transitionTime;}).duration(transitionTime)	
				      .attr("height", barHeight - 1)
			.attr("transform", function(d, i) { return "translate(" + RScale(d.superpositive+d.positive+d.neutral+d.negative) +", 0)"; });
		
		bar.append("text")
					.transition().delay(function (d,i){ return i * transitionTime;}).duration(transitionTime)	
			          .attr("x", function(d) { return RScale(d.r) + 4; })
				        .attr("y", barHeight / 2)
					      .attr("dy", ".35em")
					            .text(function(d) { return d.name; })
					.style("font-size", function(d){return barHeight/2 + "px"})
					.style("font-family", "'Source Sans Pro', sans-serif")
		
		//drawNodes(data())
	},



	ForceLayout: function(_data){
		/* The function to update svg elements if the window is being resized
		 function updateWindow(){
		 *     x = w.innerWidth || e.clientWidth || g.clientWidth;
		 *         y = w.innerHeight|| e.clientHeight|| g.clientHeight;
		 *
		 *             svg.attr("width", x).attr("height", y);
		 *             }
		 *             window.onresize = updateWindow;
		/* To Add scales to radius so that the nodes fit into the window
		 * http://alignedleft.com/tutorials/d3/scales
		 * consult the above mentioned tutorials
		 */

		_this = this;
		function DATA(value, LEVEL){return  _this.dataFunction(value, LEVEL)}
		LEVEL = 0
		var width = $(window).width() - 100;
		var height = $(window).height();

		var fill = d3.scale.category10();
		var color = d3.scale.category10().domain(d3.range(10000));


		var duration = 2000;
		var delay = 2;



		var force = d3.layout.force()
			.size([width, height])
			.charge(100)
		
		var svg = d3.select(".main-body").append("svg")
			.attr("width", width)
			.attr("height", height);

		var g = svg.append("g")
				.attr("transform", "translate(" + 0 + "," + 0 + ")")

		//This is the function wchich returns the maximum radius of the bubbles 
		function drawNodes(nodes){
			function convert_polarity(polarity){
				return polarity == 1? "positive":"negative" 

			};
		
			var RScale = d3.scale.linear()
				.domain(d3.extent(nodes, function(d) { return d.r; }))
			 	.range([width/25, 2*(width/25)])
		

			function rmax(){
				var RMAX = 0
				$.each(nodes, function(i, __node){
					if (RMAX < RScale(__node.r)){
						RMAX = RScale(__node.r)
					}
				});
				return RMAX
			}

			function tick(e){
				/*This prevents the bubbles to be dragged outside the svg element */
				node.attr("cx", function(d) { return d.x = Math.max(rmax(), Math.min(width - rmax(), d.x)); })
					        .attr("cy", function(d) { return d.y = Math.max(rmax(), Math.min(height - rmax(), d.y)); });
				
				
				var q = d3.geom.quadtree(nodes),
				i = 0,
				n = nodes.length;
				while (++i < n) q.visit(collide(nodes[i]));

					//.attr("cx", function(d) { return d.x; })
					//.attr("cy", function(d) { return d.y; })
					node
						.transition()
						.duration(75)
						.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
				};

			function collide(_node){
				var r = RScale(_node.r);
	
				nx1 = _node.x - r,
				nx2 = _node.x + r,
				ny1 = _node.y - r,
				ny2 = _node.y + r;
	    
				return function(quad, x1, y1, x2, y2){
					if (quad.point && (quad.point !== _node)){
						var x = _node.x - quad.point.x,
						y = _node.y - quad.point.y,
						l = Math.sqrt(x * x + y * y),
						r = RScale(_node.r) + RScale(quad.point.r);
						if (l < r){
							l = (l - r)/l*.5;
							_node.x -= x *= l;
							_node.y -= y *= l;
							quad.point.x += x;
							quad.point.y += y;
							}
					}
					return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;};
			
					}
		function charge(d){return RScale(d.r) + 1 }     

		force.nodes(nodes)
			.gravity(.09)
			.charge(charge)
			.start()
		force.on("tick", tick)

		var node = g.selectAll(".node")
				.data(nodes, function(d) { return d.name; })
	
	
		
		node.enter()
			.append("g")
			.attr("class", "node")
			.on("dblclick", OnDBLClick)
			.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
			.call(force.drag)
		
			
		node.append("circle")
			.attr("r", 0)
			.attr("fill", function(d, i){console.log(fill(parseInt(Math.random()*1000+ i))); return fill(parseInt(Math.random()*10+ i))}) 
			.attr("class", "node")
			//.attr("fill", function(d){return d.polarity ? "#66CCFF" : "#FF0033" }) 
			//.style("stroke", function(d, i) { return d3.rgb(fill(i & 3)).darker(10); })
			//.style("stroke", function(d, i) { return "#e377c2" })
			//.style("stroke", function(d, i) { return d.polarity == 1? "blue":"red" })
			//.style('stroke-width', '10px')
			.on("mousedown", function() { d3.event.stopPropagation(); })


		$('svg g').tipsy({ gravity: 'w', 
					html: true, 
					title: function(){
					//return  "<br>" + 'Name: ' +'  ' +'<span>' + this.__data__.name + '</span>' +"<br>" + 'Frequency: ' +  '<span>' + this.__data__.r + '</span>';}
					return   '<span>' + this.__data__.name + '</span>' + '<br>'+ '<span>' + 'Positive: ' + this.__data__.positive + '</span>' +  "<br>" + 'Negative: ' +  '<span>' + this.__data__.negative + '</span>' + '<span>' +  "<br>" + 'Neutral: ' +  '<span>'+ this.__data__.neutral + '</span>'+ '<br>'+ '<span>' + 'superpositive: '+ this.__data__.superpositive + '</span>' + '<br>'+ '<span>'+ 'supernegative: ' + this.__data__.supernegative + '</span>';}
				      });



		node.append('foreignObject')	
			.attr("class", "foreign")
			.append('xhtml:div')
			.style("font-size", 0)
			.append("p")	
		
		d3.selectAll("circle")
			.transition()
			//.duration(2000)
			.ease("cicle")
			.duration(1000) // this is 1s
			.delay(50)
			.attr("r", function(d){return RScale(d.r)})
			
		
		.transition()
		.each("end", function(){		
				d3.selectAll(document.getElementsByTagName("foreignObject")).transition()
					.attr('x', function(d){console.log(this.parentNode.getBBox()); return this.parentNode.getBBox().x/1.5})
					.attr('y', function(d){return this.parentNode.getBBox().y/2})
					.attr('width', function(d){ return 2*RScale(d.r) * Math.cos(Math.PI / 4)})
					.attr('height', function(d){ return 2*RScale(d.r) * Math.cos(Math.PI / 4)})
					.attr('color', 'black')
					.each(getSize)
			
			})

		.transition()
		.each("end", function(){		
				d3.selectAll(document.getElementsByTagName("foreignObject")).selectAll("div").transition()
					.style("font-size", function(d){return RScale(d.r)/5 + "px"})
			
			})	
			
		.transition()
		.each("end", function(){		
				d3.selectAll(document.getElementsByTagName("foreignObject")).selectAll("div").selectAll("p").transition()
					.text(function(d) { return d.name.substring(0, RScale(d.r) / 3)})
					.attr('id', "node-bubble")
					.style("text-align", "center")
					.style("vertical-align", "middle")
					.style("padding", "10px 5px 15px 20px")
					.style("line-height", "1")
			})
		

		node.exit().transition().attr("r", 0).duration(750).remove();
		
		
		d3.select("body")
			.on("mousedown", mousedown)
		
		function mousedown(){
			nodes.forEach(function(o, i){
				o.x += (Math.random() - .5) * 70;
				o.y += (Math.random() - .5) * 70;
			});
			force.resume();
		}
		
		}
		


		function getSize(d){
			var radius ;
			var bbox = this.getBBox();
			var cbbox = this.parentNode.getBBox(); 
			radius = this.parentNode.firstChild.getAttribute("r")
		}




		function OnDBLClick(d){
			/*
			LEVEL = LEVEL+1
			console.log(DATA(d.name, LEVEL))
			drawNodes(DATA(d.name, LEVEL))
			console.log(d)
			console.log(LEVEL)
			*/
			$(".sentences").empty()
			$.each(d.similar, function(iter, __data){
				__html = '<button class="btn btn-small btn-primary" type="button" style="margin: 10px">' + __data + '</button>';
				$('.sentences').append(__html)
			})
			$.each(d.sentences, function(iter, __sent){
				var subView = new App.RootRowView({model: __sent}); 
				$(".sentences").append(subView.render().el)

			})			
			console.log(d)
			console.log(d.similar)
			console.log(d.i_likeness)
			console.log(d.o_likeness)
		
		};

		console.log(DATA(null, LEVEL))
		drawNodes(DATA(null, LEVEL))
		//drawNodes(data())
	},



})



})

