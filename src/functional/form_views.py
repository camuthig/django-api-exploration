import json

from django.forms.models import ModelForm
from django.http import HttpRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from django_api.mapper.base import ModelFormMapper
from django_api.router import Router
from domain.models import Product

router = Router()


class ProductCreateForm(ModelForm):
    class Meta:
        model = Product
        fields = ["name"]


class ProductResponseForm(ModelForm):
    class Meta:
        model = Product
        fields = ["id", "name"]


class ProductCreateMapper(ModelFormMapper):
    class Meta:
        form = ProductCreateForm


class ProductResponseMapper(ModelFormMapper):
    class Meta:
        form = ProductResponseForm


@router.get("/products")
def list_products(request: HttpRequest):
    output_mapper = ProductResponseMapper()
    products = Product.objects.all()

    return JsonResponse([output_mapper.dump(p) for p in products], safe=False)

@router.post("/products")
def create_product(request: HttpRequest):
    input_mapper = ProductCreateMapper(data=json.loads(request.body))
    input_mapper.full_clean()
    input_mapper.save()

    output_mapper = ProductResponseMapper(instance=input_mapper.instance)
    return JsonResponse(output_mapper.get_data())

@router.get("/products/<int:product_id>")
def get_product(request: HttpRequest, product_id: int):
    instance = get_object_or_404(Product, pk=product_id)
    output_mapper = ProductResponseMapper(instance=instance)

    return JsonResponse(output_mapper.get_data())