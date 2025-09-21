from rest_framework import serializers

from cbv_api.models import Department
from django_api.io.drf_serializer import drf_io
from django_api.pagination import QuerySetLimitOffsetPaginator
from django_api.router import Router

router = Router()


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "title"]


class PaginatedDepartmentSerializer(serializers.Serializer):
    items = DepartmentSerializer(many=True)
    limit = serializers.IntegerField(min_value=1)
    offset = serializers.IntegerField(min_value=0)
    has_more = serializers.BooleanField()


@router.get("/departments")
@drf_io(response=PaginatedDepartmentSerializer)
def list_departments(request):
    return QuerySetLimitOffsetPaginator(10, 0, Department.objects.all())


@router.post("/departments")
@drf_io(request=DepartmentSerializer, response=DepartmentSerializer)
def create_department(request, data: DepartmentSerializer):
    instance = Department.objects.create(title=data.data["title"])

    return instance