import json

from django.http import HttpRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ninja import ModelSchema

from django_api.mapper.pydantic import PydanticModelMapper
from django_api.router import Router
from domain.models import Product

router = Router()


class ProductCreateSchema(ModelSchema):
    class Meta:
        model = Product
        fields = ["name"]


class ProductResponseSchema(ModelSchema):
    class Meta:
        model = Product
        fields = ["id", "name"]


class ProductCreateMapper(PydanticModelMapper):
    class Meta:
        model = Product
        base_model = ProductCreateSchema


class ProductResponseMapper(PydanticModelMapper):
    class Meta:
        model = Product
        base_model = ProductResponseSchema


@router.get("/products")
def list_products(request: HttpRequest):
    output_mapper = ProductResponseMapper()
    products = Product.objects.all()

    return JsonResponse([output_mapper.dump(p) for p in products], safe=False)

@router.post("/products")
def create_product(request: HttpRequest):
    input_mapper = ProductCreateMapper()
    input_mapper.load(json.loads(request.body))

    input_mapper.save()

    output_mapper = ProductResponseMapper()
    return JsonResponse(output_mapper.dump(input_mapper.instance))

@router.get("/products/<int:product_id>")
def get_product(request: HttpRequest, product_id: int):
    instance = get_object_or_404(Product, pk=product_id)
    output_mapper = ProductResponseMapper()

    return JsonResponse(output_mapper.dump(instance))