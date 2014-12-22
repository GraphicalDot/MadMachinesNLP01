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
			message: "<img src='css/images/loading_3.gif'>",
			className: "loadingclass",
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
			$(".loadingclass").modal("hide");
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
		this.model = options.model
		this._data = options.model
		this.ForceLayout(this.model);
		this.add_slide_show();
		
		/*
		var self = this;
		var jqhr = $.get(window.one_page_api)	
		//On success of the jquery post request
		jqhr.done(function(data){
			self._data = data.result
			console.log(self._data)
			self.ForceLayout(data.result);
			//self.Render(data.result);
			});

		//In case the jquery post request fails
		jqhr.fail(function(){
				bootbox.alert("Either the api or internet connection is not working, Try again later")
		});
		*/
	},

	add_slide_show: function(){$.vegas('slideshow', {
			  backgrounds:[
			{src: 'css/black-and-white-restaurant-handpainted-mural.jpg', fade:1000 }, 
			{src: 'css/chef_service.jpg', fade:1000 }, 
			{src: 'css/corn.jpg', fade:1000 }, 
			{src: 'css/Good-Restaurant-Service.jpg', fade:1000 }, 
			{src: 'css/M9ip55GcE.jpeg', fade:1000 }, 
			{src: 'css/ordering_food.jpg', fade:1000 }, 
			{src: 'css/parish-portrait.jpg', fade:1000 }, 
			{src: 'css/Queen-Vic-Market-Fresh-Food-Black-and-white.jpg', fade:1000 }, 
			{src: 'css/Rest_Interior2B.jpg', fade:1000 }, 
			{src: 'css/restaurant_kitchen.png', fade:1000 }, 
			{src: 'css/service_chef.jpg', fade:1000 }, 
			{src: 'css/tea_pot.jpg', fade:1000 }, 
			{src: 'css/The-Frenc-Laundry-Yountville-CA-iPad-Wine-Menu.jpg', fade:1000 }, 

		  ]
		})

		},

	
	olddataFunction: function  DATA(value){
			var newDataSet = [];
			if (value == null){
				$.each(this._data, function(i, __d){
					newDataSet.push({"name": __d.name, 
							"polarity": __d.polarity, 
							"r": __d.frequency*5,
							}
						)
					})
				return newDataSet
			}
			
			else{

				$.each(this._data, function(i, __d){
					if (__d.name == value){
						$.each(__d.children, function(i, _d){
							newDataSet.push({"name": _d.name, 
								"polarity": _d.polarity, 
								"r": _d.frequency*5,
								})
						})}})
					return newDataSet
			}
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
						"polarity": __d.polarity, 
						"r": __d.frequency,
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
		var width = $(window).width() - 50;
		var height = $(window).height();

		var fill = d3.scale.category10();
		var color = d3.scale.category10().domain(d3.range(10000));


		var duration = 2000;
		var delay = 2;



		var force = d3.layout.force()
			.size([width, height])
			.charge(100)
		
		var svg = d3.select("body").append("svg")
			.attr("width", width)
			.attr("height", height);

		var g = svg.append("g")
				.attr("transform", "translate(" + 0 + "," + 0 + ")")

		//This is the function wchich returns the maximum radius of the bubbles 
		function drawNodes(nodes){
				
		
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
			.style("stroke", function(d, i) { return d.polarity == 1? "blue":"red" })
			.style('stroke-width', '10px')
			.on("mousedown", function() { d3.event.stopPropagation(); })


		$('svg g').tipsy({ gravity: 'w', 
					html: true, 
					title: function(){
					//return  "<br>" + 'Name: ' +'  ' +'<span>' + this.__data__.name + '</span>' +"<br>" + 'Frequency: ' +  '<span>' + this.__data__.r + '</span>';}
					return   "<br>" + 'Frequency: ' +  '<span>' + this.__data__.r + '</span>';}
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
			LEVEL = LEVEL+1
			console.log(DATA(d.name, LEVEL))
			drawNodes(DATA(d.name, LEVEL))
			console.log(d)
			console.log(LEVEL)
		
		};

		console.log(DATA(null, LEVEL))
		drawNodes(DATA(null, LEVEL))
		//drawNodes(data())
	},







})



/*
App.WordCloudWith_D3 = Backbone.View.extend({
	initialize: function(options){
		this.model = options.model;
		console.log(this.model)
		//this.render()	
		this.copiedRender(this.model);
	},



	copiedRender: function(_data){
		var color = d3.scale.category10().domain(d3.range(_data));
		var width = $(window).width() - 50;
		var height = $(window).height()*1.3;
		format = d3.format(",d"),
		fill = d3.scale.category10();

		function DATA(value){
			var newDataSet = [];
			if (value == null){
				$.each(_data, function(i, __d){
					newDataSet.push({"name": __d.name, 
							"polarity": __d.polarity, 
							"frequency": __d.frequency,
							}
						)
					})
				return newDataSet
			}
			
			else{

				$.each(_data, function(i, __d){
					if (__d.name == value){
						$.each(__d.children, function(i, _d){
							newDataSet.push({"name": _d.name, 
								"polarity": _d.polarity, 
								"frequency": _d.frequency,
								})
						})}})
					return newDataSet
			}
		}


		var bubble = d3.layout.pack()
				.sort(null)
				.size([width, height])
				.padding(3)
				.value(function(d) {return d.size;})
 
		var svg = d3.select("body").append("svg")
					.attr("width", width)
					.attr("height", height)

		addShadow(svg)	
		
		var g = svg.append("g")
		    .attr("transform", "translate(2,2)");

	function OnClickBubble(d){
			drawBubbles(DATA(d.name))
	}	
					
	
	function drawBubbles(newData){			
		var nodes = bubble.nodes(processData(newData))
			.filter(function(d) { return !d.children; }); // filter out the outer bubble

		// assign new data to existing DOM 
		//var node = svg.selectAll('circle')
		//	.data(nodes, function(d) { return d.name; });

		// enter data -> remove, so non-exist selections for upcoming data won't stay -> enter new data -> ...

		// To chain transitions, 
		// create the transition on the updating elements before the entering elements 
		// because enter.append merges entering elements into the update selection

		var duration = 200;
		var delay = 2;

		var node = g.selectAll(".node")
				.data(nodes,  function(d) { return d.name; })
		// update - this is created before enter.append. it only applies to updating nodes.
		node.transition()
			.duration(duration)
			.delay(function(d, i) {delay = i * 7; return delay;}) 
			.attr('transform', function(d) { return 'translate(' + d.x + ',' + d.y + ')'; })
			.attr('r', function(d) { return d.r; })
			.style('opacity', 1); // force to 1, so they don't get stuck below 1 at enter()

		node.enter().append("g")
				.attr("class", "node")
				.attr('transform', function(d) { return 'translate('
						         + d.x + ',' + d.y + ')'; })
		// enter - only applies to incoming elements (once emptying data)	
		node.append('circle')
			.attr('r', function(d) { return d.r; })
			//.attr("fill", function(d){return d.className ? "#66CCFF" : "#FF0033" }) 
			.attr("fill", function(d){return color(Math.random())}) 
			.style("filter", "url(#drop-shadow)")
			.on("click", OnClickBubble)
			.attr('class', function(d) { return d.className; })
			.style('opacity', 0) 
			.transition()
			.duration(duration * 1.2)
			.style('opacity', 1);
			
		$('svg circle').tipsy({ 
					        gravity: 'w', 
					        html: true, 
					        title: function(){
							return 'Name: ' + '<span>' + this.__data__.name + '</span>';
						}
				      });


		node.append('foreignObject')
			.attr('width', function(d){ return 2 *d.r * Math.cos(Math.PI / 4)})
			.attr('height', function(d){ return 2 *d.r * Math.cos(Math.PI / 4)})
			.attr('color', 'black')
			.each(getSize)
			.append('xhtml:text')
			.text(function(d) { return d.name.substring(0, d.r / 3)})
			.attr('style', 'text-align:center')
			.attr('style', function(d) { return "font-size: " + d.r/4 })
			.transition()
			.duration(duration * 1.2)
			.style('opacity', 1);

		node.append("text")
			.attr("fill", "black")
			.style("text-anchor", "middle")
			.style("font-size", function(d) { return d.r/4 })
			.text(function(d) { return d.name.substring(0, d.r / 3); })
			.style('opacity', 0)
			.transition()
			.duration(duration * 1.2)
			.style('opacity', 1);
		// exit
		node.exit()
			.transition()
			.duration(duration + delay)
			.style('opacity', 0)
			.remove();


		}
		

		function getSize(d) {
			var radius ;
			var bbox = this.getBBox();
			cbbox = this.parentNode.getBBox();
			console.log(bbox, cbbox)
		}

		function processData(data) {
			var newDataSet = [];
			$.each(data, function(i, __d){
				console.log(__d.name, __d.frequency, __d.polarity)
				newDataSet.push({"name": __d.name, 
						"className": __d.polarity, 
						"size": __d.frequency,
						}
					)
				})
			return {"children": newDataSet};	
			}

		function addShadow(svg){
			defs = svg.append("defs");
			filter = defs.append("filter")
					.attr("id", "drop-shadow")
					.attr("height", "150%")
					.attr("width", "200%")
			
			filter.append("feGaussianBlur")
				.attr("in", "SourceAlpha")
				.attr("stdDeviation", 5)
				.attr("result", "blur");

			feOffset = filter.append("feOffset")
					.attr("in", "blur")
					.attr("dx", 5)
					.attr("dy", 5)
					.attr("result", "offsetBlur");
					
			feMerge = filter.append("feMerge");
				feMerge.append("feMergeNode")
				.attr("in", "offsetBlur")
					
			
			feMerge.append("feMergeNode")
				.attr("in", "SourceGraphic");
				}

	//This starts the bubble cloud with initial parent data
	drawBubbles(DATA(null))
	},


	

	render: function(){
		//copied from : https://github.com/vlandham/bubble_cloud/blob/gh-pages/coffee/vis.coffee
		//explanation at:

		var Bubbles, root, texts;		
		root = typeof exports !== "undefined" && exports !== null ? exports : this;
		function Bubbles(){
			var  chart, clear, click, collide, collisionPadding, connectEvents, data, force, gravity, hashchange, height, idValue, jitter, label, margin, maxRadius, minCollisionRadius, mouseout, mouseover, node, rScale, rValue, textValue, tick, transformData, update, updateActive, updateLabels, updateNodes, width
			width = $(window).width() - 50;
			height = $(window).height()*1.1;
			data = [];
			node = null;
			label = null;
			margin = {top: 5, right: 0, bottom: 0, left: 0};
			maxRadius = 80;
	
			rScale = d3.scale.sqrt().range([0,maxRadius])
	
				
			var tip = d3.tip()
				.attr('class', 'd3-tip')
				.offset([-10, 0])
				.html(function(d) {
					return "<strong style='color:black'>Frequency:</strong> <span style='color:red'>" + d.frequency + "</span>";
			    })

	
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
			minCollisionRadius = 20
	
			jitter = 0.5;

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
				node.attr("cx", function(d) { return d.x = Math.max(rScale(rValue(d)), Math.min(width - 50, d.x)); })
					.attr("cy", function(d) { return d.y = Math.max(rScale(rValue(d)), Math.min(height - 50, d.y)); });
				
				var dampenedAlpha;
				dampenedAlpha = e.alpha * 0.1

				node.each(gravity(dampenedAlpha))
				.each(collide(jitter))
				.attr("transform", function(d){
					return "translate(" + d.x + "," + d.y + ")";
				})


				texts.style("left", function(d) { return (margin.left + d.x) - d.dx / 2})
				.style("top", function(d){(margin.top + d.y) - d.dy / 2})
			};
	
	
	
			force = d3.layout.force()
					.gravity(0)
					.charge(charge)
					.size([width, height])
					.on("tick", tick)
			


			function charge(d){
				return d.frequency*d.frequency + 1

			}
	
	
			rawData = this.model
			
			function chart(selection){
				return selection
					.attr("id", "background_class")
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

					svg.call(tip)	
					
					
					//This Function will add shadow to the nodes
					addShadow(svg)	
					
					node = svgEnter.append("g")
						.attr("id", "bubble-nodes")
						.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

					node.append("rect")
						.attr("id", "bubble-background")
						.attr("width", width)
						.attr("height", height)

					update()
				})
			};


		 function update(){
			data.forEach(function(d, i){
				return d.forceR = Math.max(minCollisionRadius, rScale(rValue(d)));
			});

			updateNodes()
				};

		function getSize(d) {
			var radius ;
			var bbox = this.getBBox();
			cbbox = this.parentNode.getBBox();
			radius = this.parentNode.firstChild.getAttribute("r")	
			scale = radius/3;
			d.scale = scale;
		}


		function updateNodes(){
			node = node.selectAll(".bubble-node").data(data, function(d){ return idValue(d)})

			node.exit().remove()
			
			node.enter()
				.append("a")
				.attr("class", "bubble-node")
				.attr("fill", function(d){return d.polarity ? "#66CCFF" : "#FF0033" })
				.call(force.drag)
				.call(connectEvents)
				.append("circle")
				.attr("r", function(d){ return rScale(rValue(d))
				})
			
			//Adding tooltip
			$('svg circle').tipsy({ 
					        gravity: 'w', 
					        html: true, 
					        title: function(){
							return 'Frequency: ' + '<span>' + this.__data__.frequency + '</span>';
						}
				      });



			texts = node.append("text")
					      .style("text-anchor", "middle")
					      .attr("dy", ".3em")
					      .attr('fill', 'black')
					      .attr("label-name", function(d) { return textValue(d)})
					      .text(function(d) { return textValue(d)})
					      .each(getSize)
					      //.style("font-size", function(d){ return Math.max(1, rScale(rValue(d)/2))+"px"})
					      .style("font-size", function(d){ return d.scale+"px"})
					      .style("width", function(d){ return rScale(rValue(d))+"px"})
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
						distance = Math.sqrt(x*x+y*y)
						minDistance = d.forceR + d2.forceR + collisionPadding
          
						if (distance < minDistance){
							distance = (distance-minDistance)/distance*jitter
							moveX = x*distance
							moveY = y*distance
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
		//	d.on("click", onclick)
		};

		function onclick(d){
			console.log("Click on the bubble has been initiated")
			event.preventDefault();
			function increaseRadius(selector){
				d3.select(selector).select("circle")
					.attr("class", "clicked_bubble")
					.transition()
					.duration(7500)
					.attr("r", rScale(rValue(d))*3)
			}


			function increaseTextSize(selector){
				d3.select(selector).select("text")
					.attr("class", "clicked_bubble")
					.transition()
					.duration(7500)
					.style("font-size", function(d){ return d.scale*3+"px"});
				}



			console.log(d.frequency)
			//location.replace("#" + encodeURIComponent(idValue(d)))
			
			d3.transition()
				.ease("linear")
					.each(function() {
						d3.selectAll(".bubble-node").transition()
						.duration(7500)
				              .style("opacity", function(){ 
						      if (this.childNodes[1].getAttribute("label-name") != d.name)
						{
							return 0;
						}
						      
					      }
						      
						      )
			        })
			
					.transition()
					.ease("linear")
					.call(increaseRadius(this))

		}		    
		 tooltip = d3.select("body")
			.append("div")
			.style("position", "absolute")
			.style("z-index", "10")
			.style("visibility", "hidden")
			.text("a simple tooltip");



		function mouseover(d){
			console.log(d)
			//.tooltip({ content: "Awesome title!" });
			tooltip.text(d.name); 
			  return tooltip.style("visibility", "visible");
			return node.classed("bubble-hover", function(p){
				console.log()
				return p === d
				;
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
*/
})

