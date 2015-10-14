/* global d3 */
function radialLineChartD3(input, domEl, max) {

	var container_padding = 20,
		container_el = d3.select('#' + domEl);

	var dimensions = container_el.node().getBoundingClientRect(),
		width = dimensions.width,
		height = dimensions.height;

	var effective_width = width - container_padding * 2,
		effective_height = height - container_padding * 2;

	var twoPi = 2 * Math.PI,
		cx1 = effective_width / 2,
		cy1 = (effective_height / 2),
		gap = 14,
		baseRad = 4;

	max= 10/9*max;

	if (input.length > 7) {
		cy1 = (effective_height / 2) * (input.length / 13);
	}

	var svg = container_el.append("svg")
		.attr("width", effective_width)
		.attr("height", effective_height)
		.append("g");

	var tip = d3.tip()
		.attr('class', 'd3-tip')
		.html(function (d) {
			return "<span class='tip-title'>" + d.term + " (" + d.count + ")</span>\n<br /><div class='sexy_line'></div> <span class='tip-content'>SuperPositive: " + d.superpositive.count + "\n<br /> Positive: " + d.positive.count + "\n<br /> Neutral: " + d.neutral.count + "\n<br /> Negative: " + d.negative.count + "\n<br /> SuperNegative: " + d.supernegative.count + "</span>";
		})
		.offset([-20, 0]);

	// tip.direction('w');

	svg.call(tip);

	// Main Center Text
	svg.append("svg:text")
		.attr("font-size", "16px")
		.style("text-transform", "uppercase")
		.style("font-family", "Montserrat")
		.style("fill", "#0d47a1")
		.attr("text-anchor", "middle")
		.attr("transform", function (d, i) { return "translate(" + (cx1) + "," + (cy1 + 8) + ")"; })
		.text(domEl);

	svg.selectAll(".categories")
		.data(input)
		.enter()
		.append("svg:text")
		.filter(function(d) {
			return d.count;
		})
		.style("font-size", "14px")
		.attr("fill", "#424242")
		.attr("class", "categoryies")
		.attr("id", function(d) {return d.term.replace(/ /g,'')})
		.attr("class", "svg_Category")
		.style("font-family", "Neuton")
		.style("font-weight", "400")
		.attr("transform", function (d, i) { return "translate(" + (cx1 - 5) + "," + (cy1 - (4.3 * gap) - i * gap) + ")"; })
		.text(function (d, i) { return d.term })
		.attr("text-anchor", "end")
		.on("mouseover", function (d) {
			d3.select(this).style("fill", "#0d47a1").style("font-weight", "500")
			tip.attr('class', 'd3-tip animate').show(d, d3.select(this).node())
		})
		.on('mouseout', function (d) {
			d3.select(this).style("fill", "#424242").style("font-weight", "400")
			tip.attr('class', 'd3-tip').show(d)
			tip.hide()
		});


	var inputForRings = [], rad = baseRad;
	for (var i = 0; i < input.length; i++) {
		var ar = ["superpositive", "positive", "neutral", "negative", "supernegative"];
		var currentAngle = 0;

		var ratio = input[i].count / max, total_angle = ratio * twoPi;

		for (var j = 0; j < ar.length; j++) {

			var ringObj= merge_options({}, input[i]);
			ringObj.categoryType= ar[j];

			ringObj.startAngle = currentAngle;
			if (input[i].count !== 0) {
				ringObj.endAngle = currentAngle + total_angle * (input[i][ar[j]].count / input[i].count);
				currentAngle += total_angle * (input[i][ar[j]].count / input[i].count);
			} else {
				ringObj.endAngle = currentAngle;
			}

			ringObj.innerRadius = 5 + gap * rad;
			ringObj.outerRadius = 5 + gap * rad + 1;
			ringObj.color = input[i][ar[j]].color;
			inputForRings.push(ringObj);
		}

		rad++;
	}

	svg.selectAll(".p0")
		.data(inputForRings)
		.enter()
		.append("path")
		.filter(function(d) {
			return d[d.categoryType].count;
		})
		.each(rings)

	function rings(d, i) {
		var arc = d3.svg.arc()
			.startAngle(function (d) { return d.startAngle })
			.innerRadius(function (d) { return d.innerRadius })
			.outerRadius(function (d) { return d.outerRadius })
			.endAngle(function (d) { return d.endAngle });
		d3.select(this)
			.attr("transform", "translate(" + cx1 + "," + cy1 + ")")
			.attr("d", arc)
			.style("fill", function (d) {
				return d.color;
			})
			.style("stroke", function(d) {
				return d.color
			})
			.style("stroke-width", 1)
			.on("mouseover", function (d) {
				var legend_node= d3.select("#"+d.term.replace(/ /g,''));
				legend_node.style("fill", "#0d47a1").style("font-weight", "500")
				tip.attr('class', 'd3-tip animate').show(d, legend_node.node())
			})
			.on("mouseout", function (d) {
				var legend_node= d3.select("#"+d.term.replace(/ /g,''));
				legend_node.style("fill", "#424242").style("font-weight", "400")
				tip.attr('class', 'd3-tip').show(d)
				tip.hide()
			});
	}

	rad= baseRad;
	svg.selectAll(".c0")
		.data(inputForRings)
		.enter()
		.append("circle")
		.filter(function(d) {
			return d[d.categoryType].count;
		})
		.each(circles);

	function circles(d, i) {
		d3.select(this)
			.attr("transform", "translate(" + cx1 + "," + cy1 + ")")
			.attr("cx", function (d, i) { return (d.innerRadius) * Math.cos(d.endAngle - twoPi / 4); })
			.attr("cy", function (d, i) { return (d.innerRadius) * Math.sin(d.endAngle - twoPi / 4); })
			.style("fill", function(d) {
				return d.color
			})
			.on("mouseover", function(d) {
				var legend_node= d3.select("#"+d.term.replace(/ /g,''));
				legend_node.style("fill", "#0d47a1").style("font-weight", "500")
				tip.attr('class', 'd3-tip animate').show(d, legend_node.node())
			})
			.on("mouseout", function(d) {
				var legend_node= d3.select("#"+d.term.replace(/ /g,''));
				legend_node.style("fill", "#424242").style("font-weight", "400")
				tip.attr('class', 'd3-tip').show(d)
				tip.hide()
			})
			.attr("r", 3);
	}

	function merge_options(obj1, obj2) {
    var obj3 = {};
    for (var attrname in obj1) { obj3[attrname] = obj1[attrname]; }
    for (var attrname in obj2) { obj3[attrname] = obj2[attrname]; }
    return obj3;
	}
}