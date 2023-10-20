from django.urls import path
from . import views

app_name = 'invoice'

urlpatterns = [
    path('', views.index, name='index'),
    path('createInvoice/', views.createInvoice, name='createInvoice'),
    path("invoiceHistory/", views.invoiceHistory, name="invoiceHistory"),
    path("addProductsClients/", views.addProductsClients, name="addProductsClients"),

] 