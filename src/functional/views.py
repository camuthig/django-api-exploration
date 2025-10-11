from django.http import HttpRequest
from django.http import JsonResponse

from django_api.router import Router

router = Router()

@router.get("/products")
def list_products(request: HttpRequest):
    return JsonResponse({"Hello": "World"})

@router.post("/products")
def create_product(request: HttpRequest):
    return JsonResponse({"Create": "World"})

@router.get("/products/<int:product_id>")
def get_product(request: HttpRequest, product_id: int):
    return JsonResponse({"Get": product_id})