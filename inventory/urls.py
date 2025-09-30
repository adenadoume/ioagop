from django.urls import path
from . import views
app_name = "inventory"
urlpatterns = [

    path("attachments/<str:target>/<int:pk>/", views.attachments_list, name="attachments_list"),
    path("attachments/delete/<int:pk>/", views.attachment_delete, name="attachment_delete"),

    path("", views.grid, name="grid"),
    path("container/<int:container_id>/", views.grid, name="container_grid"),
    path("reorder/<int:container_id>/", views.reorder_items, name="reorder_items"),
    path("inline/<str:model>/<int:pk>/<str:field>/", views.inline_update, name="inline_update"),
    path("attach/<str:target>/<int:pk>/", views.attach_upload, name="attach_upload"),
    path("import/xlsx/", views.xlsx_import, name="xlsx_import"),
]
