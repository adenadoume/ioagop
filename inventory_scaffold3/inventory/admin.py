from django.contrib import admin
from django.db.models import Sum, F
from .models import Supplier, Product, Container, ContainerItem, Attachment, Project, Building
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    search_fields = ("name", "email", "phone")
    list_display = ("name", "email", "phone")
class ContainerItemInline(admin.TabularInline):
    model = ContainerItem
    extra = 0
    autocomplete_fields = ("product",)
@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    inlines = [ContainerItemInline]
    search_fields = ("code",)
    list_display = ("code", "departure_date", "arrival_date", "supplier")
    list_filter = ("supplier",)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "supplier", "project", "building", "weight_kg", "cbm", "unit_cost")
    list_filter = ("supplier", "project", "building")
    search_fields = ("name", "sku", "supplier__name", "project__name", "building__name")
    autocomplete_fields = ("supplier", "project", "building")
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    search_fields = ("name",)
@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("name", "project")
    search_fields = ("name", "project__name")
    autocomplete_fields = ("project",)
@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "size", "product", "container")
    search_fields = ("name", "content_type")
