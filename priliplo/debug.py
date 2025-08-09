from django.utils.deprecation import MiddlewareMixin
from django.views.debug import ExceptionReporter
from django.views.debug import technical_500_response
import sys

class UserBasedExceptionMiddleware(ExceptionReporter):
    def get_traceback_data(self):
        data = super().get_traceback_data()
        # print("----------------------------------")
        # print(data)
        return data

    # def process_exception(self, request, exception):
    #     print("----------------------------------")
    #     print(request.user)
    #     return None

from django.http import HttpResponse
class UserBasedExceptionMiddleware1(MiddlewareMixin):
    def process_exception(self, request, exception):
        print (request.user)
        if request.user.is_superuser:
            return None
        else:
            return HttpResponse("Произошла ошибка.")

        # if request.user.is_superuser:
        #     return technical_500_response(request, *sys.exc_info())
