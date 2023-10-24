from django import forms
from invoice.models import *
from django.forms import formset_factory
import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class WorkOrderForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all(), empty_label=None)
    
    # You can add more fields here as needed


class WorkOrderItemForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        empty_label="Select a Product",
        label="Product"
    )
    description = forms.CharField(max_length=200, label="Description")
    


WorkOrderItemFormSet = formset_factory(WorkOrderItemForm, extra=1)

class WorkOrderItemFormEdit(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity']


class WorkOrderItemOtherForm(forms.ModelForm):
    class Meta:
        model = WorkOrderItem
        fields = ['workOrder', 'product', 'custom_product_name', 'custom_product_description', 'number']
        widgets = {
            'workOrder': forms.HiddenInput(),
            'product': forms.HiddenInput(),
            'number': forms.HiddenInput(),
        }
    

    def clean_custom_product_description(self):
        description = self.cleaned_data.get('custom_product_description')

        if len(description) > 100:
            raise ValidationError("Description can't be longer than 100 characters.")

        return description



class WorkOrderEnrichmentForm(forms.Form):
    is_rush = forms.BooleanField(required=False)
    return_by = forms.DateField(
    required=False,
    widget=forms.DateInput(attrs={'class': 'form-control datepicker', 'style': 'width: 125px;'})
)
    quote_required = forms.BooleanField(required=False)
    specialInstructions = forms.CharField(max_length=250, required=False)

class WorkOrderItemFormEdit(forms.ModelForm):
    class Meta:
        model = WorkOrderItem
        fields = ['product']

'''
# Add fields for custom product
custom_product_name = models.CharField(max_length=200, blank=True, null=True)
custom_product_description = models.TextField(blank=True, null=True)
custom_product_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
'''
