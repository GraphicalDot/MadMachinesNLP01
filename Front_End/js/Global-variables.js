	
$(document).ready(function(){
	App = {} ;
	window.App = App ;
	window.template = function(name){ return Mustache.compile($("#"+name+"-template").html()); };
	window.make_request = function make_request(data){ url =  window.process_text_url ; return $.post(url, {"text": data}) }
	//window.URL = "http://localhost:8000/"
	window.URL = "http://ec2-50-112-147-199.us-west-2.compute.amazonaws.com:8080/"
	
	window.process_text_url = window.URL + "process_text";
	window.update_model_url = window.URL + "update_model";
	window.update_review_error = window.URL + "update_review_error";
	window.update_customer = window.URL + "update_customer";
	window.eateries_list = window.URL + "eateries_list";
	window.eateries_details = window.URL + "eateries_details";
	window.update_review_classification = window.URL + "update_review_classification";
	window.get_ngrams = window.URL + "get_ngrams";
	window.upload_noun_phrases = window.URL + "upload_noun_phrases";
	window.upload_interjection_error = window.URL + "upload_interjection_error";
	window.get_reviews_count = window.URL + "get_reviews_count";	
	window.get_start_date_for_restaurant = window.URL + "get_start_date_for_restaurant";	
	window.get_word_cloud = window.URL + "get_word_cloud";
	window.compare_algorithms = window.URL + "compare_algorithms";


});
