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
        empty_label="Select an Instrument",
        label="Instrument"

    )
    description = forms.CharField(max_length=200, label="Description")
    quantity = forms.IntegerField(min_value=1)
    mfgnum = forms.CharField(max_length=50, label="Description")
    

WorkOrderItemFormSet = formset_factory(WorkOrderItemForm, extra=1)

class WorkOrderViewForm(forms.Form):
    STATUS_CHOICES = [
        ('Waiting_on_Assignment', 'Waiting on Assignment'),
        ('Checked_Out', 'Checked Out'),
        ('Needs_QC', 'Needs QC'),
        ('Parts_On_Order', 'Parts On Order'),
        ('QC_PASS', 'QC PASS'),
        ('QC_FAIL', 'QC FAIL'),
    ]

    QC_STATUS_CHOICES = [
        ('QC_FAIL', 'QC FAIL'),
        ('QC_PASS', 'QC PASS'),
        ('WAITING_QC', 'Waiting On QC'),
        ('NO_QC', ' ')
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label='Status',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False  # Make the field optional
    )
    technician = forms.ModelChoiceField(
        queryset=User.objects.all(),
        to_field_name='id',
        empty_label='Select a Technician',
        label='Technician',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False  # Make the field optional
    )
    qc = forms.ChoiceField(
        choices=QC_STATUS_CHOICES,
        label='QC',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False  # Make the field optional
    )
    item_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    

WorkOrderViewFormSet = formset_factory(WorkOrderViewForm, extra=1)

class WorkOrderItemFormEdit(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity']




class WorkOrderItemOtherForm(forms.ModelForm):
    mfgnum = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'maxlength': '12'}), label="Manufacturer #") 
    custom_product_name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'maxlength': '20'}), label="Name")
    quantity = forms.IntegerField(min_value=1)
    custom_product_description = forms.CharField(label="Description",max_length=40,required=False,
                                                 widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}))


    class Meta:
        model = WorkOrderItem
        fields = ['workOrder', 'product', 'quantity', 'mfgnum', 'custom_product_name', 'custom_product_description', 'number']
        widgets = {
            'workOrder': forms.HiddenInput(),
            'product': forms.HiddenInput(),
            'number': forms.HiddenInput(),
        }

    # ... rest of your form ...

    def clean_custom_product_description(self):
        description = self.cleaned_data.get('custom_product_description')

        if len(description) > 100:
            raise ValidationError("Description can't be longer than 100 characters.")

        return description



class WorkOrderEnrichmentForm(forms.Form):
    is_rush = forms.BooleanField(required=False, label="RUSH?", widget=forms.CheckboxInput(attrs={'style': 'height: 40px; margin: 5px'}))
    return_by = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}), label="RETURN BY:")
    quote_required = forms.BooleanField(required=False, label="QUOTE?", widget=forms.CheckboxInput(attrs={'style': 'height: 40px; margin: 5px'}))
    specialInstructions = forms.CharField(max_length=250, required=False, label="SPECIAL INSTRUCTIONS", widget=forms.Textarea(attrs={'rows': 1, 'cols': 40}))
    
    account_contact = forms.ModelChoiceField(
        queryset=ClientContact.objects.none(),
        required=False,
        label="ACCOUNT CONTACT",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Contact"  # Set the default text here
    )
    
    def __init__(self, *args, **kwargs):
        # Retrieve the additional variable from kwargs
        client_id = kwargs.pop('client_id', None)

        super(WorkOrderEnrichmentForm, self).__init__(*args, **kwargs)

        # Modify the queryset of the account_contact field based on the passed client_id
        if client_id is not None:
            self.fields['account_contact'].queryset = ClientContact.objects.filter(client__id=client_id)

    

class WorkOrderItemDelete(forms.ModelForm):
    class Meta:
        model = WorkOrderItem
        fields = ['id']

class WorkOrderItemFormEdit(forms.ModelForm):
    class Meta:
        model = WorkOrderItem
        fields = ['product']

class SignatureForm(forms.ModelForm):
    class Meta:
        model = Signature
        fields = ['image']