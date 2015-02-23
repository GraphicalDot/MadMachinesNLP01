#-*- coding: utf-8 -*-
from ProcessingCeleryTask import ReviewIdToSentTokenize, MappingList, SentTokenizeToNP

def call_celery(eatery_id, category, start_epoch,  end_epoch, tag_analysis_algorithm, sentiment_analysis_algorithm, 
        word_tokenization_algorithm, pos_tagging_algorithm, noun_phrases_algorithm):
        result = list()
        celery_chain = (ReviewIdToSentTokenize.s(eatery_id, category, start_epoch, end_epoch, tag_analysis_algorithm, 
                    sentiment_analysis_algorithm)|  MappingList.s(word_tokenization_algorithm, pos_tagging_algorithm, 
                        noun_phrases_algorithm, SentTokenizeToNP.s()))()
        print celery_chain
        ##Waitng for the ReviewIdToSentTokenize task to finish
        while celery_chain.status != "SUCCESS":
                pass

        ##Waiting for the SentTokenizeToNP tasks to finish
        for id in celery_chain.children[0]:
                while id.status != "SUCCESS":
                        pass


        ##Te above code gurantees that all the SentTokenizeToNP has been finished and now we can gather reult of these
        ##tasks
        for id in celery_chain.children[0]:
                result.append(id.get())

        ##Deleting all the results from the backends
        ids =  [__id.id for __id in celery_chain.children[0]]
        ids.extend([celery_chain.parent.id, celery_chain.id])

        CleanResultBackEnd.apply_async(args=[ids])
        return result




