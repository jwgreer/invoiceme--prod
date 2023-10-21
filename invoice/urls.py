from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'invoice'

urlpatterns = [
    path('', views.landingPage, name='landingPage'),
    path('home/', views.home, name='home'),
    path('createInvoice/', views.createInvoice, name='createInvoice'),
    path('createInvoice2/', views.createInvoice2, name='createInvoice2'),
    path("invoiceHistory/", views.invoiceHistory, name="invoiceHistory"),
    path("addProductsClients/", views.addProductsClients, name="addProductsClients"),
    path('addItems/<int:invoice_id>/', views.addItems, name='addItems'),
    path("createClient/", views.createClient, name="createClient"),
    path('products/createProduct/', views.createProduct, name="createProduct"),
    path('products/createProductType/', views.createProductType, name="createProductType"),
    #path('register/', views.registerPage, name="registerPage"),
    path('login/', views.loginPage, name="loginPage"),
    path('logout/', views.logoutUser, name="logout"),
    path('check-login/', views.check_login, name='check_login'),



    path('invoice/api/createInvoice/', views.createInvoiceAPI, name='createInvoiceAPI'),
    path('invoice/api/invoiceAll/', views.invoiceAllAPI, name="invoiceAllAPI"),
    path('invoice/api/itemInvoice/<int:invoice_pk>/', views.itemInvoiceAPI, name="itemInvoiceAPI"),
    path('invoice/api/productsID/<int:id>/', views.productsIDAPI, name="productsIDAPI"),
    path('invoice/api/clientAll/', views.clientsAllAPI, name="clientAllAPI"),
    path('invoice/api/newestProduct/<int:invoice_pk>/', views.newestProductAPI, name="newestProductAPI"),
    path('invoice/api/editInvoiceItem/<int:invoice_pk>/<int:id>/', views.editInvoiceItemAPI, name="editInvoiceItemAPI"),
    path('invoice/api/deleteInvoiceItem/<int:id>/', views.deleteInvoiceItemAPI, name="deleteInvoiceItemAPI"),

] 