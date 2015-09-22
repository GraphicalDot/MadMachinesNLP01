#!/usr/bin/python 
import jsonrpclib
from simplejson import loads
import nltk
from nltk import Tree
from nltk.draw.util import CanvasFrame
from nltk.draw import TreeWidget
from nltk.corpus import wordnet

server = jsonrpclib.Server("http://localhost:3456")

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







def save_tree(sentence):
        result = loads(server.parse(sentence))
        tree = result["sentences"][0]["parsetree"]
        cf = CanvasFrame()
        name = hashlib.md5(sentence).hexdigest()

        t = nltk.tree.Tree.fromstring(tree) 
        tc = TreeWidget(cf.canvas(), t)
        cf.add_widget(tc, 10,10) # (10,10) offsets
        cf.print_to_file('{0}.ps'.format(name))
        cf.destroy()
        return 







def wordnet_meaning(word):
        __word_meaning = wordnet.synsets(word)[0]
        if not __word_meaning:
                print "No word meaning found for this word"
                return False


        __word_meaning.definition()
        __word_meaning.examples()







if __name__ == "__main__":
        save_tree("Then i went to this place") 
