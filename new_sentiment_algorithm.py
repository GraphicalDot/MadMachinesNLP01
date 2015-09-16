#!/usr/bin/python 
import json
import urllib

from nltk.corpus import wordnet

def showsome(searchfor):
        query = urllib.urlencode({'q': searchfor})
        url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
        search_response = urllib.urlopen(url)
        search_results = search_response.read()
        results = json.loads(search_results)
        data = results['responseData']
        print 'Total results: %s' % data['cursor']['estimatedResultCount']
        hits = data['results']
        print 'Top %d hits:' % len(hits)
        for h in hits: 
                print h['titleNoFormatting'], h["url"]
                
        print 'For more results, see %s' % data['cursor']['moreResultsUrl']





def wordnet_meaning(word):
        __word_meaning = wordnet.synsets(word)[0]
        if not __word_meaning:
                print "No word meaning found for this word"
                return False


        __word_meaning.definition()
        __word_meaning.examples()







if __name__ == "__main__":
        showsome("freaked") 
