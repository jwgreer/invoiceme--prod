import django_filters 
from .models import *
from django_filters import CharFilter, NumberFilter
from django.db.models import Q
import re


class ClientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Client Name')

    class Meta:
        model = Client
        fields = ['name']

class ProductsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Instrument Name')
    product_type = django_filters.ModelChoiceFilter(
        field_name='product_type', queryset=ProductType.objects.exclude(name="Other"), label='Instrument Type' # exclude the other option
        #field_name='product_type', queryset=ProductType.objects.all(), label='Product Type'
    )

    class Meta:
        model = Product
        fields = ['name', 'product_type']


