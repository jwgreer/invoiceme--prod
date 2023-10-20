from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'invoice'

urlpatterns = [
    path('', views.index, name='index'),
    path('createInvoice/', views.createInvoice, name='createInvoice'),
    path("invoiceHistory/", views.invoiceHistory, name="invoiceHistory"),
    path("addProductsClients/", views.addProductsClients, name="addProductsClients"),
    path('addItems/<int:invoice_id>/', views.addItems, name='addItems'),



    path('invoice/api/createInvoice/', views.createInvoiceAPI, name='createInvoiceAPI'),
    path('api/invoiceAll/', views.invoiceAllAPI, name="invoiceAllAPI"),
    path('itemInvoice/<int:invoice_pk>/', views.itemInvoiceAPI, name="itemInvoiceAPI"),

    path('api/clientAll/', views.clientsAllAPI, name="clientAllAPI"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)