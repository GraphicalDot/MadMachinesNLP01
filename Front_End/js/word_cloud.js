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

	loading_bootbox: function(){
		$(".data_selection").modal("hide");
		bootbox.dialog({ 
			closeButton: false, 
			message: "<img src='css/images/gangam.gif'>",
			className: "loading_dialogue",
		});
	},

	submit: function(event){
		var self = this;
		$(".dynamic_display_word_cloud").empty();	
		event.preventDefault();
		this.$el.addClass("dvLoading");
	
		this.loading_bootbox()


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
		
		
		//On success of the jquery post request
		jqhr.done(function(data){
			var subView = new App.WordCloudWith_D3({model: data.result});
			$(".loading_dialogue").modal("hide");
			});

		//In case the jquery post request fails
		jqhr.fail(function(){
				bootbox.alert("Either the api or internet connection is not working, Try again later")
				self.$el.removeClass("dvLoading");
				event.stopPropagation();
		});

	
	},





	cancel: function(event){
		event.preventDefault();
		$(".data_selection").modal("hide");
	},

});

App.WordCloudWith_D3 = Backbone.View.extend({
	initialize: function(options){
		this.model = options.model;
		console.log(this.model)
		this.render();
	},


	render: function(){
		//copied from : https://github.com/vlandham/bubble_cloud/blob/gh-pages/coffee/vis.coffee
		//explanation at:

		var Bubbles, root, texts;		
		root = typeof exports !== "undefined" && exports !== null ? exports : this;
		function Bubbles(){
			var  chart, clear, click, collide, collisionPadding, connectEvents, data, force, gravity, hashchange, height, idValue, jitter, label, margin, maxRadius, minCollisionRadius, mouseout, mouseover, node, rScale, rValue, textValue, tick, transformData, update, updateActive, updateLabels, updateNodes, width
			width = $(window).width();
			height = $(window).height();
			data = [];
			node = null;
			label = null;
			margin = {top: 5, right: 0, bottom: 0, left: 0};
			maxRadius = 65;
	
			rScale = d3.scale.sqrt().range([0,maxRadius])
	
	
			function rValue(d){
				return parseInt(d.frequency);
				};

			function idValue(d){
				return d.name
				};
	
			function textValue(d){
				return d.name
					};

			collisionPadding = 4
			minCollisionRadius = 12
	
			jitter = 0.5

			transformData = function(rawData){
				rawData.forEach(function(d){
					d.count = parseInt(d.count);
						return rawData.sort(function(){
							return 0.5 - Math.random();
										});
				})
					return rawData;
					  };
		

			function tick(e){
			
				var dampenedAlpha;
				dampenedAlpha = e.alpha * 0.1
				console.log

				node.each(gravity(dampenedAlpha))
				.each(collide(jitter))
				.attr("transform", function(d){
					return "translate(" + d.x + "," + d.y + ")";
				})
		
				return label.style("left", function(d){
					return ((margin.left + d.x) - d.dx / 2) + "px";
						}).style("top", function(d) {
							return ((margin.top + d.y) - d.dy/2) + "px";
						});
					
			};
	
	
	
			force = d3.layout.force()
					.gravity(0)
					.charge(0)
					.alpha(0.5)
					.size([width, height])
					.on("tick", tick)

	
	
	
			rawData = this.model

			function chart(selection){
				return selection
					.attr("class", "background_class")
					.each(function(rawData){
					var maxDomainValue, svg, svgEnter;
					data = transformData(rawData)
					maxDomainValue = d3.max(data, function(d){ return rValue(d)})
					rScale.domain([0, maxDomainValue])
		
					svg = d3.select(this)
						.selectAll("svg")
						.data([data])
				





					svgEnter = svg.enter().append("svg");
					svg.attr("width", width + margin.left + margin.right);
					svg.attr("height", height + margin.top + margin.bottom);	      
	      	
					node = svgEnter.append("g")
						.attr("id", "bubble-nodes")
						.attr("transform", "translate(" + margin.left + "," + margin.top + ")");


					defs = svg.append("defs");
				

					filter = defs.append("filter")
						    .attr("id", "drop-shadow")
						    .attr("height", "150%")
						    .attr("width", "200%")
					// SourceAlpha refers to opacity of graphic that this filter will be applied to
					// // convolve that with a Gaussian with standard deviation 3 and store result
					// // in blur
					filter.append("feGaussianBlur")
						.attr("in", "SourceAlpha")
						.attr("stdDeviation", 5)
						.attr("result", "blur");

					feOffset = filter.append("feOffset")
						    .attr("in", "blur")
						        .attr("dx", 5)
							    .attr("dy", 5)
							        .attr("result", "offsetBlur");

					// overlay original SourceGraphic over translated blurred opacity by using
					// // feMerge filter. Order of specifying inputs is important!
					feMerge = filter.append("feMerge");
							feMerge.append("feMergeNode")
							.attr("in", "offsetBlur")
					
					feMerge.append("feMergeNode")
						.attr("in", "SourceGraphic");


					node.append("rect")
						.attr("id", "bubble-background")
						.attr("width", width)
						.attr("height", height)
						.on("click", clear)

					label = d3.select(this)
						.selectAll("#bubble-labels")
						.data([data])
						.enter()
						.append("div")
						.attr("id", "bubble-labels")
					update()
					hashchange()
					
					
					return d3.select(window).on("hashchange", hashchange)
				})
			};


		 function update(){
			data.forEach(function(d, i){
				return d.forceR = Math.max(minCollisionRadius, rScale(rValue(d)));
			});
			force.nodes(data).start()
			updateNodes()
			return updateLabels()
				};

		function updateNodes(){
			node = node.selectAll(".bubble-node").data(data, function(d){ return idValue(d)})
			node.exit().remove()
			
			return node.enter()
				.append("a")
				.style("filter", "url(#drop-shadow)")
				.attr("class", "bubble-node")
				.attr("fill", function(d){return d.polarity ? "#66CCFF" : "#FF0033" })
				//.attr("fill", "url(#gradientForegroundPurple)")
				.attr("xlink:href", function(d) {
					return "#" + (encodeURIComponent(idValue(d)))})
				.call(force.drag)
				.call(connectEvents)
				.append("circle")
				.attr("r", function(d){ return rScale(rValue(d))
				})

		}
	

		function updateLabels(){
			var labelEnter;
			label = label.selectAll(".bubble-label").data(data, function(d){ return idValue(d)})
			label.exit().remove()


			/*Here we can see that each label is an a with two div elements inside it. One to hold the 
			 * word/phrase name, the other to hold the count. We will look at how these anchors work in 
			 * the next section.
			 */
			labelEnter = label.enter().append("a")
					.attr("class", "bubble-label")
					.attr("href", function(d){ return "#" + (encodeURIComponent(idValue(d)))})
					.call(force.drag)
					.call(connectEvents)
					
			labelEnter.append("div")
				.attr("class", "bubble-label-name")
				.text(function(d){ return textValue(d)})

			labelEnter.append("div")
				.attr("class", "bubble-label-value")
				.text(function(d){ return rValue(d)})

			label.style("font-size", function(d){ return Math.max(8, rScale(rValue(d)/2))+"px"})
				.style("width", function(d){ return 2.5*rScale(rValue(d))+"px"})

			label.append("span")
				.text(function(d){return textValue(d)})
				.each(function(d) {return d.dx = Math.max(2.5 * rScale(rValue(d)), this.getBoundingClientRect().width)})
				.remove()

			label.style("width", function(d){return d.dx + "px"})
  
			return label.each(function(d){return d.dy = this.getBoundingClientRect().height
			})
		}

		function gravity(alpha){
			cx = width/2
			cy = height/2
			ax = alpha/8
			ay = alpha

			return function(d){
				d.x += (cx - d.x)*ax
				return d.y += (cy - d.y)*ay
				};
		};


		function collide(jitter){
			return function(d){
				return data.forEach(function(d2){
					var distance, minDistance, moveX, moveY, x, y;
					
					if (d != d2){
						x = d.x - d2.x
						y = d.y - d2.y
						distance = Math.sqrt(x * x + y * y)
						minDistance = d.forceR + d2.forceR + collisionPadding
          
						if (distance < minDistance){
							distance = (distance - minDistance) / distance * jitter
							moveX = x * distance
							moveY = y * distance
							d.x -= moveX
							d.y -= moveY
							d2.x += moveX
							d2.y += moveY
						}
					}
						})
				}
					}


		function connectEvents(d){
			d.on("click", click)
			d.on("mouseover", mouseover)
			return d.on("mouseout", mouseout)
		};

		function clear(){
			return location.replace("#")
				};
				
		function click(d){
			//location.replace("#" + encodeURIComponent(idValue(d)))
				return d3.event.preventDefault()
			};

		function hashchange(){
			var id;
			id = decodeURIComponent(location.hash.substring(1)).trim()
			return updateActive(id)
			};

		function updateActive(id){
			node.classed("bubble-selected", function(d) {
				return id === idValue(d);
				});
			if (id.length > 0){
				return d3.select("#status").html("<h3>The word <span class=\"active\">" + id + "</span> is now active</h3>");
				}else{
					return d3.select("#status").html("<h3>No word is active</h3>");
				}
				  };

		function mouseover(d){
			console.log(d)
			return node.classed("bubble-hover", function(p){
				return p === d;
			});
			      };
		function mouseout(d){
			return node.classed("bubble-hover", false);
			        };

		  chart.jitter = function(_) {
			      if (!arguments.length) {
				            return jitter;
					        }
			          jitter = _;
				      force.start();
				          return chart;
					    };
		    chart.height = function(_) {
			        if (!arguments.length) {
					      return height;
					          }
				    height = _;
				        return chart;
					  };
		      chart.width = function(_) {
			          if (!arguments.length) {
					        return width;
						    }
				      width = _;
				          return chart;
					    };
		        chart.r = function(_) {
				    if (!arguments.length) {
					          return rValue;
						      }
				        rValue = _;
					    return chart;
					      }


		return chart

		}
		
		plotData = function(selector, data, plot){
			return d3.select(selector).datum(data).call(plot);
		};
		 
		
		plot = Bubbles();

		plotData(".dynamic_display", this.model, plot);

	},
})

})

