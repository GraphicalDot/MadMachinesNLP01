from elasticsearch import Elasticsearch, helpers 
from colored import fg, bg, attr
import time
import datetime

ES_CLIENT = Elasticsearch("localhost", timeout=30)
try:
        ES_CLIENT.indices.create(index="zomatoscraping")
except Exception as e:
        print e
        pass




def print_messege(status, messege, function_name, error=None, eatery_id=None, eatery_url=None, review_id=None):

        if status=="success":
                __messege = "{0}{1}SUCCESS: {2}{3}{4} from Func_name=<<{5}>> eatery_id=<<{6}>>, review_id=<<{7}>> \
                        eatery_url=<<8>> {9}".format(fg("black"), bg('dark_green'), attr("reset"), \
                        fg("dark_green"), messege, function_name, eatery_id, review_id, eatery_url, attr("reset"))
                print __messege
        elif status == "info":
                __messege = "{0}{1}INFO: {2}{3}{4} from Func_name=<<{5}>> with error<<{6}>> eatery_id=<<{7}>>, \
                        review_id=<<{8}>>, eatery_url=<<{9}>>{10}".format(fg("black"), bg('white'), attr("reset"), \
                        fg(202), messege, function_name, error, eatery_id, review_id, eatery_url, attr("reset"))

                print __messege
        try:
                error_message = error.message
        except:
                error_message = None

        result = {"status": status,
                "function_name": function_name,
                "error": error_message,
                "eatery_id": eatery_id,
                "review_id": review_id,
                "eatery_url": eatery_url,
                "messege": messege,
                "generated": time.time(),
                "generated_utc": datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y"),
                "error_name": e.__class__.__name__,
                }

        ES_CLIENT.index(index="zomatoscraping", doc_type="celerylogs", body=result) 
        return 


def process_result(__dict, dom_string):
        """
        Process the result returned, in other words converts the result returned from ES
        into a json which will be used by front end
        """
        def wrap(func):
                def wrapper(*args, **kwargs):
                        try:
                                result = func(*args, **kwargs)
                        except Exception as e:
                                print_messege("error", "Erorr occurred", func.__name__, e, __dict["eatery_id"], eatery_url=__dict["eatery_url"], review_id=None)
                                result = None

                        __dict[dom_string] = result
                        return __dict
                return wrapper
        return wrap

