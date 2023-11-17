from rest_framework import serializers
from invoice.models import *

class workOrderColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrders
        fields = ['workOrder_num','color']

class workOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrders
        fields = ['workOrder_num','client','workOrder_date','items','status', 'created_by']


class workOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderItem
        fields = ['id', 'workOrder', 'product', 'description', 'quantity','status','color', 'mfgnum', 'number', 'custom_product_name', 'custom_product_description', 'issue']

    def validate_quantity(self, value):
        if value is None or value < 1:
            raise serializers.ValidationError("Quantity must be 1 or greater.")
        return value

class workOrderItemOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderItem
        fields = ['id', 'workOrder', 'product', 'quantity','custom_product_name', 'color', 'mfgnum', 'custom_product_description', 'issue']

class workOrderItemNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderItem
        fields = ['number']


class workOrderItemOtherNameSerializer(serializers.ModelSerializer):
    product_type = serializers.PrimaryKeyRelatedField(source='product', read_only=True)
    name = serializers.PrimaryKeyRelatedField(source='custom_product_name', read_only=True)
    description = serializers.PrimaryKeyRelatedField(source='custom_product_description', read_only=True)
    price = serializers.PrimaryKeyRelatedField(source='custom_product_price', read_only=True)

    class Meta:
        model = WorkOrderItem
        fields = ['id', 'name', 'description','price', 'product_type']