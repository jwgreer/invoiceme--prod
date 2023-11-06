from django import forms
from .models import Client, Product, Invoice, ProductType, Product, InvoiceItem, ClientContact
from django.forms import formset_factory
import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone


class InvoiceForm2(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'invoice_date', 'items', 'status']  # Add other fields as needed


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User  # Use 'model' instead of 'models'
        fields = ['username', 'email', 'password1', 'password2']

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'address']


class ClientContactForm(forms.ModelForm):
    class Meta:
        model = ClientContact
        fields = ['first_name', 'last_name', 'phone', 'email', 'client']

class ClientSelectionForm(forms.Form):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        empty_label="Select a Client",
        label="Select a Client"
    )

class InvoiceItemForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        empty_label="Select a Product",
        label="Product"
    )
    quantity = forms.IntegerField(min_value=1, label="Quantity", error_messages={'min_value': 'Quantity must be at least 1'})
    


InvoiceItemFormSet = formset_factory(InvoiceItemForm, extra=1)


class InvoiceForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all(), empty_label=None)
    # You can add more fields here as needed


class ProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = ['name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'product_type']
        labels = {
            'product_type': 'Instrument Type',
        }

class InvoiceItemFormEdit(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity']

