from django.http import HttpRequest
from django.http import JsonResponse

from django_api.router import Router

router = Router()

@router.get("/departments")
def list_departments(request: HttpRequest):
    return JsonResponse({"Hello": "World"})

@router.post("/departments")
def create_department(request: HttpRequest):
    return JsonResponse({"Create": "World"})

@router.get("/departments/<int:department_id>")
def get_department(request: HttpRequest, department_id: int):
    return JsonResponse({"Get": department_id})