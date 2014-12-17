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
		/*
		this.model = options.model
		this._data = options.model
		this.ForceLayout(this.model);
	*/
		//this.add_slide_show();
		
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
		 * function updateWindow(){
		 *     x = w.innerWidth || e.clientWidth || g.clientWidth;
		 *         y = w.innerHeight|| e.clientHeight|| g.clientHeight;
		 *
		 *             svg.attr("width", x).attr("height", y);
		 *             }
		 *             window.onresize = updateWindow;
		 */
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
		var color = d3.scale.category10().domain(d3.range(_data));


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
			function rmax(){
				var RMAX = 0
				$.each(nodes, function(i, __node){
					if (RMAX < __node.r){
						RMAX = __node.r
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
					node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
				};

			function collide(_node){
				var r = _node.r + 160;
	
				nx1 = _node.x - r,
				nx2 = _node.x + r,
				ny1 = _node.y - r,
				ny2 = _node.y + r;
	    
				return function(quad, x1, y1, x2, y2){
					if (quad.point && (quad.point !== _node)){
						var x = _node.x - quad.point.x,
						y = _node.y - quad.point.y,
						l = Math.sqrt(x * x + y * y),
						r = _node.r + quad.point.r;
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
		function charge(d){return d.frequency*d.frequency + 1 }     

		force.nodes(nodes)
			.gravity(.09)
			.charge(charge)
			.start()
		force.on("tick", tick)

		var node = g.selectAll(".node")
				.data(nodes, function(d) { return d.name; })
	
	
		node.transition()
			.duration(duration)
			.delay(function(d, i) {delay = i * 7; return delay;}) 
			.style('opacity', 0) 
			.attr('r', function(d) { return d.r; })
			.style('opacity', 1); // force to 1, so they don't get stuck below 1 at enter()
		
		node.enter()
			.append("g")
			.attr("class", "node")
			.on("dblclick", OnDBLClick)
			.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; })
			.call(force.drag)
				      
		node.append("circle")
			.attr("r", function(d){return d.r})
			.attr("fill", function(d){return color(Math.random())}) 
			.attr("class", "node")
			//.attr("fill", function(d){return d.polarity ? "#66CCFF" : "#FF0033" }) 
			.style("stroke", function(d, i) { return d3.rgb(fill(i & 3)).darker(10); })
			.on("mousedown", function() { d3.event.stopPropagation(); })
		
			
		$('svg g').tipsy({ gravity: 'w', 
					html: true, 
					title: function(){
					return  "<br>" + 'Name: ' +'  ' +'<span>' + this.__data__.name + '</span>';}
				      });


		node.append('foreignObject')
			.attr('x', function(d){return this.parentNode.getBBox().x/1.5})
			.attr('y', function(d){return this.parentNode.getBBox().y/2})
			.attr('width', function(d){ return 2*d.r * Math.cos(Math.PI / 4)})
			.attr('height', function(d){ return 2*d.r * Math.cos(Math.PI / 4)})
			.attr('color', 'black')
			.each(getSize)
			.append('xhtml:div')
			.style("font-size", function(d){return d.r/4.2 + "px"})
			.append("p")
			.text(function(d) { return d.name.substring(0, d.r / 3)})
			.attr('id', "node-bubble")
			.style("text-align", "center")
			.style("vertical-align", "middle")
			.style("padding", "10px 5px 15px 20px")
			.style("line-height", "1")

		
		node.exit().remove();
		
		
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


		drawNodes(DATA(null, LEVEL))
		//drawNodes(data())
	},





	OldRender: function(_data){
		_this = this;
		function DATA(value, LEVEL){return  _this.dataFunction(value, LEVEL)}
		LEVEL = 0
		var color = d3.scale.category10().domain(d3.range(_data));
		var width = $(window).width() - 50;
		var height = $(window).height();
		format = d3.format(",d"),
		fill = d3.scale.category10();
		
		


		var bubble = d3.layout.pack()
				.sort(null)
				.size([width, height])
				.padding(3)
				.value(function(d) {return d.size;})
 
		var svg = d3.select(".container-fluid").append("svg")
					.attr("width", width)
					.attr("height", height)

		addShadow(svg)	
		
		var g = svg.append("g")
		    .attr("transform", "translate(2,2)");

	function OnClickBubble(d){
			LEVEL = LEVEL +1
			console.log("Here is the pre4sent level or dept at which we are in " +LEVEL)
			drawBubbles(DATA(d.name, LEVEL))
	}	
					
	
	function drawBubbles(newData){	
		var nodes = bubble.nodes(processData(newData))
			.filter(function(d) { return !d.children; }); // filter out the outer bubble


		var duration = 2000;
		var delay = 2;

		var node = g.selectAll(".node")
				.data(nodes,  function(d) { return d.name; })
		node.transition()
			.duration(duration)
			.delay(function(d, i) {delay = i * 7; return delay;}) 
			.style('opacity', 0) 
			.attr('r', function(d) { return d.r; })
			.style('opacity', 1); // force to 1, so they don't get stuck below 1 at enter()

		node.enter().append("g")
				.attr("class", "node")
				.attr('transform', function(d) { return 'translate('
							         + d.x + ',' + d.y + ')'; })
		
		node.append('circle')
			.attr('r', function(d) { return d.r; })
			//.attr("fill", function(d){return d.className ? "#66CCFF" : "#FF0033" }) 
			.attr("fill", function(d){return color(Math.random())}) 
			.style("filter", "url(#drop-shadow)")
			.on("click", OnClickBubble)
			.attr('class', function(d) { return d.className; })
			.style('opacity', 0) 
			.transition()
			.duration(duration)
			.style('opacity', 1);
			
		$('svg circle').tipsy({ gravity: 'w', 
					html: true, 
					title: function(){
					return 'Name: ' + '<span>' + this.__data__.name + '</span>';}
				      });


		node.append('foreignObject')
			.attr('x', function(d){return this.parentNode.getBBox().x/1.5})
			.attr('y', function(d){return this.parentNode.getBBox().y/2})
			.attr('width', function(d){ return 2*d.r * Math.cos(Math.PI / 4)})
			.attr('height', function(d){ return 2*d.r * Math.cos(Math.PI / 4)})
			.attr('color', 'black')
			.each(getSize)
			.append('xhtml:div')
			.style("font-size", function(d){return d.r/4.2 + "px"})
			.append("p")
			.on("click", OnClickBubble)
			.text(function(d) { return d.name.substring(0, d.r / 3)})
			.attr('id', "node-bubble")
			.style("text-align", "center")
			.style("vertical-align", "middle")
			.style("padding", "10px 5px 15px 20px")
			.style("line-height", "1")
			.style('opacity', 0) 
			.transition()
			.duration(duration)
			.style('opacity', 1);

		node.exit()
			.transition()
			.duration(duration)
			.style('opacity', 0)
			.remove();


		}
	
		function getSize(d){
			var radius ;
			var bbox = this.getBBox();
			var cbbox = this.parentNode.getBBox(); 
			radius = this.parentNode.firstChild.getAttribute("r")
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
	drawBubbles(DATA(null, LEVEL))
	},


})

})

