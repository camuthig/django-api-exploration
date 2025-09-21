from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from pydantic import BaseModel
from pydantic import ConfigDict

from cbv_api.models import Department
from django_api.io.pydantic_adapter import LimitOffsetPaginationModel
from django_api.io.pydantic_adapter import LimitOffsetPaginationQueryModel
from django_api.io.pydantic_adapter import pydantic_io
from django_api.io.response import APIResponse
from django_api.pagination import QuerySetLimitOffsetPaginator
from django_api.router import Router

router = Router()

class DepartmentModel(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)

@router.get("/departments")
@pydantic_io(request=LimitOffsetPaginationQueryModel, response=LimitOffsetPaginationModel[DepartmentModel])
def list_departments(request: HttpRequest, data: LimitOffsetPaginationQueryModel):
    response = APIResponse(QuerySetLimitOffsetPaginator(data.limit, data.offset, Department.objects.all()))

    # An example of adding custom headers to the response
    response["X-Total-Count"] = Department.objects.count()

    return response

class CreateDepartmentModel(BaseModel):
    title: str

    model_config = ConfigDict(str_strip_whitespace=True)


@router.post("/departments")
@pydantic_io(request=CreateDepartmentModel, response=DepartmentModel)
def create_department(request: HttpRequest, data: CreateDepartmentModel):
    instance = Department.objects.create(title=data.title)

    return instance


@router.get("/departments/<int:department_id>")
@pydantic_io(response=DepartmentModel)
def get_department(request: HttpRequest, department_id: int):
    return get_object_or_404(Department, pk=department_id)
