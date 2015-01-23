#!/usr/bin/env python
import difflib
import copy
        

def merging_if_one_common_element(original_list):
        """
        
        
        
        """
        
        original_dict = {element.get("name"): {"frequency": element.get("frequency"), "polarity": element.get("polarity")} \
					for element in original_list}
			
			
        calc_simililarity = lambda __a, __b: difflib.SequenceMatcher(a=__a.get("name").lower(), b=__b.get("name").lower()).ratio() \
										if __a.get("name").lower() != __b.get("name").lower() else 0
			
			
	list_with_similarity_ratios = list()
	for test_element in original_list:
	        for another_element in copy.copy(original_list):
		        r = calc_simililarity(test_element, another_element)	
			list_with_similarity_ratios.append(dict(test_element.items() +  
					{"similarity_with": another_element.get("name"), "ratio": r}.items()))

			

	
def merging_similar_elements(original_list):
        """
        This function will calculate the minum distance between two noun phrase and if the distance is 
        less than 1 and more than .8, delete one of the element and add both their frequencies
        """
        
        original_dict = {element.get("name"): {"frequency": element.get("frequency"), "polarity": element.get("polarity")} \
					for element in original_list}
			
			
        calc_simililarity = lambda __a, __b: difflib.SequenceMatcher(a=__a.get("name").lower(), b=__b.get("name").lower()).ratio() \
										if __a.get("name").lower() != __b.get("name").lower() else 0
			
			
	list_with_similarity_ratios = list()
	for test_element in original_list:
	        for another_element in copy.copy(original_list):
		        r = calc_simililarity(test_element, another_element)	
			list_with_similarity_ratios.append(dict(test_element.items() +  
					{"similarity_with": another_element.get("name"), "ratio": r}.items()))

			

	
        filtered_list = [element for element in list_with_similarity_ratios if element.get("ratio") <1 and element.get("ratio") > .8]



			
	for element in filtered_list:
		try:
		        requency = original_dict[element.get("name")]["frequency"] + \
					original_dict[element.get("similarity_with")]["frequency"]
							
			del original_dict[element.get("similarity_with")]
			original_dict[element.get("name")]["frequency"] = frequency
					
		except Exception as e:
			pass

	"""
	##This is when you want to subtract and add frequency based on the polarity
	for element in filtered_list:
		try:
			if original_dict[element.get("similarity_with")]["polarity"] == 0:
				frequency = original_dict[element.get("name")]["frequency"] - original_dict[element.get("similarity_with")]["frequency"]
			else:
			        frequency = original_dict[element.get("name")]["frequency"] + original_dict[element.get("similarity_with")]["frequency"]

				del original_dict[element.get("similarity_with")]
				original_dict[element.get("name")]["frequency"] = frequency
					
		except Exception as e:
			pass
	"""
	result = list()

	
	for k, v in original_dict.iteritems():
	        l = {"name": k.upper()}
		l.update(v)
		result.append(l)

			
	return  result
