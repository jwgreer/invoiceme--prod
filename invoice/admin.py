from django.contrib import admin
from .models import *

admin.site.register(Client)
admin.site.register(ClientContact)
admin.site.register(Product)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(ProductType)
admin.site.register(Discount)
admin.site.register(Tax)
admin.site.register(WorkOrders)
admin.site.register(Signature)
admin.site.register(Color)

@admin.register(WorkOrderItem)
class WorkOrderItemAdmin(admin.ModelAdmin):
    list_display = ('workOrder', 'product', 'quantity', 'description', 'number', 'custom_product_name', 'created_by','custom_product_description', 'custom_product_price')
    list_filter = ('workOrder', 'product', 'quantity')
    search_fields = ('workOrder__name', 'description', 'number', 'custom_product_name')


# Register your models here.
