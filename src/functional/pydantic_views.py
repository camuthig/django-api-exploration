from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from pydantic import BaseModel
from pydantic import ConfigDict

from django_api.io.pydantic_protocol import LimitOffsetPaginationModel
from django_api.io.pydantic_protocol import LimitOffsetPaginationQueryModel
from django_api.io.pydantic_protocol import json_protocol
from django_api.io.response import APIResponse
from django_api.pagination import QuerySetLimitOffsetPaginator
from django_api.router import Router
from domain.models import Department

router = Router()


class DepartmentModel(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)

@router.get("/departments")
@json_protocol(request=LimitOffsetPaginationQueryModel, response=LimitOffsetPaginationModel[DepartmentModel])
def list_departments(request: HttpRequest, data: LimitOffsetPaginationQueryModel):
    response = APIResponse(QuerySetLimitOffsetPaginator(data.limit, data.offset, Department.objects.all()))

    # An example of adding custom headers to the response
    response["X-Total-Count"] = Department.objects.count()

    return response

class CreateDepartmentModel(BaseModel):
    title: str

    model_config = ConfigDict(str_strip_whitespace=True)


@router.post("/departments")
@json_protocol(request=CreateDepartmentModel, response=DepartmentModel)
def create_department(request: HttpRequest, data: CreateDepartmentModel):
    instance = Department.objects.create(title=data.title)

    return instance


@router.get("/departments/<int:department_id>")
@json_protocol(response=DepartmentModel)
def get_department(request: HttpRequest, department_id: int):
    return get_object_or_404(Department, pk=department_id)
