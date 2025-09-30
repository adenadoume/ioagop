from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
class Supplier(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    def __str__(self): return self.name
class Project(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, default="general")
    def __str__(self): return self.name
class Building(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="buildings")
    name = models.CharField(max_length=200)
    def __str__(self): return f"{self.project.name} / {self.name}"
class Product(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=120, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=12, decimal_places=3, blank=True, null=True)
    cbm = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    building = models.ForeignKey(Building, null=True, blank=True, on_delete=models.SET_NULL)
    meta = models.JSONField(default=dict, blank=True)
    def __str__(self): return self.name
class Container(models.Model):
    code = models.CharField(max_length=64, unique=True)
    departure_date = models.DateField(blank=True, null=True)
    arrival_date = models.DateField(blank=True, null=True)
    supplier = models.ForeignKey(Supplier, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True, null=True)
    def __str__(self): return self.code
class ContainerItem(models.Model):
    container = models.ForeignKey(Container, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="container_items")
    quantity = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    class Meta: unique_together = ("container", "product")
    @property
    def total_weight(self): return (self.product.weight_kg or 0) * self.quantity
    @property
    def total_cbm(self): return (self.product.cbm or 0) * self.quantity
    @property
    def total_cost(self): return (self.product.unit_cost or 0) * self.quantity
class Attachment(models.Model):
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE, related_name="attachments")
    container = models.ForeignKey(Container, null=True, blank=True, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="attachments/%Y/%m/")
    name = models.CharField(max_length=255, blank=True)
    size = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=120, blank=True)
    def save(self, *args, **kwargs):
        try: self.size = self.file.size
        except Exception: pass
        super().save(*args, **kwargs)
