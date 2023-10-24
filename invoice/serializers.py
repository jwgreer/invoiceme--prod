from rest_framework import serializers
from .models import Invoice, Client, InvoiceItem, Product


class invoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['invoice_num','client','invoice_date','items','status']


class invoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id','invoice', 'product', 'quantity', 'number']

class invoiceItemNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['number']


class clientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['name','email','phone','address']



class productSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id',"name", "description", "price", "product_type"]