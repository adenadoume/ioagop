from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from .models import Supplier, Product, Container, ContainerItem, Attachment, Project, Building
from .forms import AttachmentForm, XLSXUploadForm
@login_required
def grid(request, container_id=None):
    context = {}
    if container_id:
        container = get_object_or_404(Container, pk=container_id)
        items = (ContainerItem.objects
                 .select_related("product", "product__supplier")
                 .filter(container=container)
                 .order_by("order", "id"))
        totals = items.aggregate(
            total_kg=Sum(F("quantity") * F("product__weight_kg")),
            total_cbm=Sum(F("quantity") * F("product__cbm")),
            total_cost=Sum(F("quantity") * F("product__unit_cost")),
        )
        context.update(container=container, items=items, totals=totals, mode="container")
    else:
        products = Product.objects.select_related("supplier", "project", "building").all().order_by("id")
        totals = products.aggregate(
            total_kg=Sum("weight_kg"),
            total_cbm=Sum("cbm"),
            total_cost=Sum("unit_cost"),
        )
        context.update(products=products, totals=totals, mode="products")
    return render(request, "inventory/grid.html", context)
@login_required
@require_POST
def reorder_items(request, container_id):
    container = get_object_or_404(Container, pk=container_id)
    import json
    try:
        data = json.loads(request.body.decode("utf-8"))
        ids = data.get("order", [])
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")
    order_map = {int(id_): idx for idx, id_ in enumerate(ids)}
    for item in ContainerItem.objects.filter(container=container, id__in=order_map.keys()):
        item.order = order_map[item.id]
        item.save(update_fields=["order"])
    return JsonResponse({"ok": True})
@login_required
@require_POST
def inline_update(request, model, pk, field):
    MODEL = {"product": Product, "item": ContainerItem}.get(model)
    if not MODEL: return HttpResponseBadRequest("Bad model")
    obj = get_object_or_404(MODEL, pk=pk)
    value = request.POST.get("value", "").strip()
    from decimal import Decimal
    try:
        f = MODEL._meta.get_field(field)
        if f.get_internal_type() in ("DecimalField", "FloatField"):
            setattr(obj, field, Decimal(value or "0"))
        elif f.get_internal_type() in ("IntegerField", "PositiveIntegerField"):
            setattr(obj, field, int(value or "0"))
        else:
            setattr(obj, field, value)
        obj.save(update_fields=[field])
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    return JsonResponse({"ok": True, "id": obj.id, field: value})
@login_required
def attach_upload(request, target, pk):
    obj = get_object_or_404(Product if target == "product" else Container, pk=pk)
    if request.method == "POST":
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            att = form.save(commit=False)
            if target == "product": att.product = obj
            else: att.container = obj
            att.name = att.file.name
            att.content_type = getattr(att.file, 'content_type', '') or ''
            att.save()
            if request.headers.get("HX-Request"):
                return render(request, "inventory/_attachments_list.html", {"object": obj})
            return redirect("inventory:grid")
    else:
        form = AttachmentForm()
    return render(request, "inventory/attach_upload.html", {"form": form, "object": obj})
@login_required
def xlsx_import(request):
    if request.method == "POST":
        form = XLSXUploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data["file"]
            try:
                import pandas as pd
                df = pd.read_excel(f)
            except Exception as e:
                return HttpResponseBadRequest(f"Read error: {e}")
            created = 0; updated = 0
            for _, row in df.iterrows():
                supplier, _ = Supplier.objects.get_or_create(name=str(row.get("supplier")).strip())
                proj_name = str(row.get("project")).strip() if row.get("project") else None
                bld_name = str(row.get("building")).strip() if row.get("building") else None
                project = None; building = None
                if proj_name:
                    project, _ = Project.objects.get_or_create(name=proj_name)
                    if bld_name:
                        building, _ = Building.objects.get_or_create(project=project, name=bld_name)
                sku = str(row.get("sku")).strip() if row.get("sku") else None
                defaults = dict(
                    supplier=supplier,
                    weight_kg=row.get("weight_kg") or None,
                    cbm=row.get("cbm") or None,
                    unit_cost=row.get("unit_cost") or None,
                    project=project, building=building,
                )
                name = str(row.get("name")).strip()
                prod, was_created = Product.objects.update_or_create(
                    supplier=supplier, name=name, defaults=defaults
                )
                created += int(was_created); updated += int(not was_created)
            return JsonResponse({"ok": True, "created": created, "updated": updated})
    else:
        form = XLSXUploadForm()
    return render(request, "inventory/xlsx_import.html", {"form": form})


from django.views.decorators.http import require_http_methods

@login_required
def attachments_list(request, target, pk):
    obj = get_object_or_404(Product if target == "product" else Container, pk=pk)
    return render(request, "inventory/_attachments_list.html", {"object": obj})

@login_required
@require_http_methods(["DELETE"])
def attachment_delete(request, pk):
    att = get_object_or_404(Attachment, pk=pk)
    parent = att.product or att.container
    att.delete()
    # Return nothing for hx-swap=outerHTML to remove the chip
    return HttpResponse(status=204)
