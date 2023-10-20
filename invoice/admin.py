from django.contrib import admin
from .models import *

admin.site.register(Client)
admin.site.register(Product)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(ProductType)
admin.site.register(Discount)
admin.site.register(Tax)

# Register your models here.
