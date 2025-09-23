from django.http import JsonResponse

from django_api.router import Router

router = Router()

@router.get("/stuff")
def get_stuff(request):
    return JsonResponse({"List": "stuff"})


@router.post("/stuff")
def post_stuff(request):
    return JsonResponse({"Post": 1})


@router.get("/stuff/<int:id>")
def get_stuff_id(request, id):
    return JsonResponse({"Get": id})


@router.put("/stuff/<int:id>")
def put_stuff_id(request, id):
    return JsonResponse({"Put": id})


@router.delete("/stuff/<int:id>")
def delete_stuff_id(request, id):
    return JsonResponse({"Delete": id})
