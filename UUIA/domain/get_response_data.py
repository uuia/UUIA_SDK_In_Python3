#@writer : zhongbr
#@filename:
#@purpose:

from ..exception.lack_necessary_info_exception import Lack_necessary_info_exception
from ..exception.action_callback_exception import Callback_exception


def get_response_data(group, action, request, form, callbacks):
    if form.get("uuid") != None:
        callback_path = "{}/{}".format(group, action)
        callback_func = callbacks.get(callback_path)
        if callback_func == None:
            raise Callback_exception(
                "The callback function of action:\"{}\" for group:\"{}\" is not existing .".format(action, group))
        response = callback_func(form, request)
        if not response.get("uuid"):
            raise Lack_necessary_info_exception("In response of action '{}' , an uuid for user is needed !".format(action))
        return response
    else:
        raise Lack_necessary_info_exception("There isn't a string of uuid from the request from center server.")