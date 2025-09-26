from django.http import JsonResponse
from django.views import View

from django_api.router import Router

router = Router()


"""
An example of using only the router with a generic class-based view.

There is not concept for parsing or rendering used here outside of what is provided by JsonResponse.
The purpose of using the router in this way is to allow grouping it with a higher level concept (not yet implemented) that
allows combining a group of routers into a consistent API. This would allow for that higher level concept to possibly 
control things like error handling and authentication, which is often best defined across the entire API.
"""


class MultiActionView(View):
    def get(self, request):
        return JsonResponse({"List": "stuff"})

    def post(self, request):
        return JsonResponse({"Post": 1})

    def put(self, request):
        return JsonResponse({"Put": 1})

    def patch(self, request):
        return JsonResponse({"Patch": 1})

    def delete(self, request):
        return JsonResponse({"Delete": 1})


router.add_view("/stuff", ["GET", "POST", "PUT", "PATCH", "DELETE"], MultiActionView)