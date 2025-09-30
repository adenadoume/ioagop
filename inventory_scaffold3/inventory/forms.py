from django import forms
from .models import Attachment
class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ["file"]
class XLSXUploadForm(forms.Form):
    file = forms.FileField(help_text="Upload .xlsx file with columns: supplier,name,sku,weight_kg,cbm,unit_cost,project,building")
