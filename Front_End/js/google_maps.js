$(document).ready(function(){
console.log("wwbvwovw");
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else { 
        console.log("Geolocation is not supported by this browser.");
    }
}

function showPosition(position) {
    console.log("Latitude: " + position.coords.latitude + "Longitude: " + position.coords.longitude);	
}
      	console.log("Am i fucking with someone")
	getLocation();
	function initialize() {
	              var mapCanvas = document.getElementById('map-canvas');
		              var mapOptions = {
				                center: new google.maps.LatLng('28.6427138889', '77.1192555556'),
							          zoom: 12,
								            mapTypeId: google.maps.MapTypeId.ROADMAP
										            }
			              var map = new google.maps.Map(mapCanvas, mapOptions)
map.set('styles', [
{
    featureType: 'road',
    elementType: 'geometry',
    stylers: [
      { color: '#000000' },
      { weight: 1.6 }
    ]
  }, {
    featureType: 'road',
    elementType: 'labels',
    stylers: [
      { saturation: -100 },
      { invert_lightness: true }
    ]
  }, {
    featureType: 'landscape',
    elementType: 'geometry',
    stylers: [
      { hue: '#ffff00' },
      { gamma: 1.4 },
      { saturation: 82 },
      { lightness: 96 }
    ]
  },
{
    featureType: 'poi',
    elementType: 'geometry',
    stylers: [
      { hue: '#fff700' },
      { lightness: -15 },
      { saturation: 99 }
    ]
  }
]);
		__array = [{'name': 'Cheese Chaplin', 'coordinates': [28.5244611111, 77.1919944444]}, {'name': 'Chef &amp; I', 'coordinates': [28.5246305556, 77.1914527778]}, {'name': 'Cafe Seclude', 'coordinates': [28.5245277778, 77.1909777778]}, {'name': 'Shroom', 'coordinates': [28.524948, 77.190225]}, {'name': 'Lure Switch', 'coordinates': [28.5291066667, 77.1936133333]}]
		var markers= []
	 	$.each(__array, function(iter, data){
				marker = new google.maps.Marker({
				map: map,
				position: new google.maps.LatLng(data.coordinates[0], data.coordinates[1]),
				title: data.name
    				})
	
				markers.push(marker)
				google.maps.event.addListener(marker, 'click', function() {
						map.setZoom(11);
    						map.setCenter(marker.getPosition());
  						});
		
    				markers[markers.length - 1]['infowin'] = new google.maps.InfoWindow({
    	   	 		content: '<div>This is a marker in ' + data.name + '</div>'
    				});
			})

					            }
		google.maps.event.addDomListener(window, 'load', initialize);


		});
