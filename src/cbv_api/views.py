# Create your views here.
from django.http import JsonResponse
from django.views import View

from django_api.router import Router

"""
For routing conventions, I can't use the non-generic views. Each of `ListView`, `DetailView`, etc.
has to be on their own URL pattern in Django, which is a bit of a dealbreaker from a REST convention
perspective. I need two endpoints:

* List/Create: /myResources
* Detail/Update/Delete: /myResources/:id

We can register each of these views with the router to handle that for us.
"""

# Using things like `CreateView` is a headache. You have to overwrite how the form kwargs are instantiated and push the
# `data` context for the response and overwrite the response_class to be JsonResponse.
# And even then, it tries to redirect somewhere, which isn't helpful.
# In my opinion, it isn't worth trying to get Create/Edit/Delete working with REST with all the extra overhead.


class DepartmentListView(View):
    def get(self, request):
        return JsonResponse({"List": "OK"})


class DepartmentCreateView(View):
    def post(self, request):
        return JsonResponse({"Create": "OK"})


router = Router()

# Either of these patterns work
router.get("/departments")(DepartmentListView.as_view())
router.add_view("/departments", ["POST"], DepartmentCreateView)
