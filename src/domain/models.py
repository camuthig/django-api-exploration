from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=100)


class Warehouse(models.Model):
    name = models.CharField(max_length=100)


class ProductInventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="inventory")
    quantity = models.IntegerField()