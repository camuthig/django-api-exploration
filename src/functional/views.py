from django.http import HttpRequest
from django.http import JsonResponse
from pydantic import BaseModel
from pydantic import ConfigDict

from cbv_api.models import Department
from django_api.io.pydantic_adapter import pydantic_io
from django_api.router import Router

router = Router()

class DepartmentModel(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


@router.get("/departments")
def list_departments(request: HttpRequest):
    return JsonResponse({"Hello": "World"})

class CreateDepartmentModel(BaseModel):
    title: str

    model_config = ConfigDict(str_strip_whitespace=True)


@router.post("/departments")
@pydantic_io(request=CreateDepartmentModel, response=DepartmentModel)
def create_department(request: HttpRequest, data: CreateDepartmentModel):
    instance = Department.objects.create(title=data.title)

    return instance


@router.get("/departments/<int:department_id>")
def get_department(request: HttpRequest, department_id: int):
    return JsonResponse({"Get": department_id})