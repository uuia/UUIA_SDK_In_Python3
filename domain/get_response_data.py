#@writer : zhongbr
#@filename:
#@purpose:

from repository.repository_index import get_resopne_index_dict
from exception.lack_necessary_info_exception import Lack_necessary_info_exception

def get_response_data(action,request):
    if request.form.get("uuid") != None:
        response = get_resopne_index_dict[action]().get_data(request)
        if not response.get("uuid"):
            raise Lack_necessary_info_exception("In response of action '{}' , an uuid for user is needed !".format(action))
        return response
    else:
        raise Lack_necessary_info_exception("There isn't a string of uuid from the request from center server.")