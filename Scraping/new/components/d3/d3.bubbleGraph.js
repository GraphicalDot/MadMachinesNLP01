/* global d3 */
function truncate(str, maxLength, suffix) {
	if (str.length > maxLength) {
		str = str.substring(0, maxLength + 1);
		str = str.substring(0, Math.min(str.length, str.lastIndexOf(" ")));
		str = str + suffix;
	}
	return str;
}


function d3BubbleGraph(data, domEl) {
	var margin = { top: 20, right: 200, bottom: 0, left: 20 },
		width = 250,
		height = 400,
		padding= 20,
		keys = ['super-negative', 'negative', 'neutral', 'positive', 'super-positive'];

	height= (height*(data.length+1))/20;
	var	container_el = d3.select('#' + domEl);

	var dimensions = container_el.node().getBoundingClientRect();
	width = dimensions.width- margin.right- margin.left- (padding*2);
	// height = dimensions.height;

	// container_el.attr(height, height);

	var svg = container_el.append("svg")
		.attr("width", width + margin.left + margin.right+ (padding*2))
		.attr("height", height + margin.top + margin.bottom+ (padding*2))
		.style("margin-left", margin.left + "px")
		.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	var c = d3.scale.category20c();

	var xScale = d3.scale.ordinal()
		.domain(keys)
		.rangePoints([margin.left, width]);
	//		.rangeRoundBands([0, width], 0.05);

	var xAxis = d3.svg.axis().scale(xScale).orient("top");

	svg.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + 0 + ")")
		.call(xAxis);

	for (var i = 0; i < data.length; i++) {
		var g = svg.append("g").attr("class", "journal");

		var circleTextData = [
			[keys[0], data[i][keys[0]]], [keys[1], data[i][keys[1]]], [keys[2], data[i][keys[2]]], [keys[3], data[i][keys[3]]], [keys[4], data[i][keys[4]]]
		];

		var circles = g.selectAll("circle")
			.data(circleTextData)
			.enter()
			.append("circle");

		var text = g.selectAll("text")
			.data(circleTextData)
			.enter()
			.append("text");

		var rScale = d3.scale.linear()
			.domain([0, d3.max(circleTextData, function (d) { return d[1] })])
			.range([2, 9]);

		circles
			.attr("cx", function (d, i) { return xScale(d[0]); })
			.attr("cy", i * 20 + 20)
			.attr("r", function (d) { return rScale(d[1]); })
			.style("fill", function (d) { return c(i); });

		text
			.attr("y", i * 20 + 25)
			.attr("x", function (d, i) { return xScale(d[0]) - 5; })
			.attr("class", "value")
			.text(function (d) { return d[1]; })
			.style("fill", function (d) { return c(i); })
			.style("display", "none");

		g.append("text")
			.attr("y", i * 20 + 25)
			.attr("x", width + 20)
			.attr("class", "label")
			.text(truncate(data[i]['name'], 30, "...") + "-(" + data[i].total_sentiments + ")")
			.style("fill", function (d) { return c(i); })
			.on("mouseover", mouseover)
			.on("mouseout", mouseout);
	}

	function mouseover(p) {
		var g = d3.select(this).node().parentNode;
		d3.select(g).selectAll("circle").style("display", "none");
		d3.select(g).selectAll("text.value").style("display", "block");
	}

	function mouseout(p) {
		var g = d3.select(this).node().parentNode;
		d3.select(g).selectAll("circle").style("display", "block");
		d3.select(g).selectAll("text.value").style("display", "none");
	}
}