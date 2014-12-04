$(document).ready(function(){


App.WordCloudWith_D3 = Backbone.View.extend({
	initialize: function(options){
		var self = this;
		var jqhr = $.get(window.one_page_api)	
		//On success of the jquery post request
		jqhr.done(function(data){
			self.copiedRender(data.result);
			});

		//In case the jquery post request fails
		jqhr.fail(function(){
				bootbox.alert("Either the api or internet connection is not working, Try again later")
		});
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
			.style('opacity', 0) 
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
			.append('xhtml:text')
			.text(function(d) { return d.name.substring(0, d.r / 3)})
			.attr('style', function(d) { return "font-size: " + d.r/4 })
			.attr('id', "node-bubble")
			.style('opacity', 0) 
			.transition()
			.duration(duration * 1.2)
			.style('opacity', 1);

		/*
		node.append("text")
			.attr("fill", "black")
			.style("text-anchor", "middle")
			.style("font-size", function(d) { return d.r/4 })
			.text(function(d) { return d.name.substring(0, d.r / 3); })
			.style('opacity', 0)
			.transition()
			.duration(duration * 1.2)
			.style('opacity', 1);
		*/
		// exit
		node.exit()
			.transition()
			.duration(duration + delay)
			.style('opacity', 0)
			.remove();


		}
	
		function getSize(d){
			var radius ;
			var bbox = this.getBBox();

			cbbox = this.parentNode.getBBox();
			console.log(bbox, cbbox, this.getBoundingClientRect(), d.name )
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


})

})

