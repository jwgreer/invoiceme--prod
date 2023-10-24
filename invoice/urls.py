from django.urls import path
from . import views
from trackingCard import views as trackingCardViews
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
    path('editInvoiceItem/<int:invoice_pk>/<int:id>/', views.editInvoiceItem, name="editInvoiceItem"),
    path("pdf/<int:invoice_id>", views.pdf, name="pdf"),
    path("createClient/", views.createClient, name="createClient"),
    path("createClientContact/", views.createClientContact, name="createClientContact"),
    path('products/createProduct/', views.createProduct, name="createProduct"),
    path('products/createProductType/', views.createProductType, name="createProductType"),
    
    
    #path('register/', views.registerPage, name="registerPage"),
    path('login/', views.loginPage, name="loginPage"),
    path('logout/', views.logoutUser, name="logout"),
    path('check-login/', views.check_login, name='check_login'),
    
    
    path('trackingCardsPDF/<int:workOrder_id>', trackingCardViews.pdfTracker, name='pdfTracker'),
    path('customerTrackingPDF/<int:workOrder_id>', trackingCardViews.pdfCustomerTracking, name='pdfCustomerTracking'),
    path('shopWorkDashboard/', trackingCardViews.shopWorkDashboard, name='shopWorkDashboard'),
    path('createWorkOrder/', trackingCardViews.createWorkOrder, name='createWorkOrder'),
    path('addItemsWorkOrder/<int:workOrder_id>/', trackingCardViews.addItemsWorkOrder, name='addItemsWorkOrder'),
    path('customWorkOrderItem/<int:workOrder_id>/', trackingCardViews.customWorkOrderItem, name="customWorkOrderItem"),
    path('workOrderEnrichmentForm/<int:workOrder_id>/', trackingCardViews.workOrderEnrichmentForm, name="workOrderEnrichmentForm"),
    path('editWorkOrderItem/<int:workOrder_id>/<int:id>/', trackingCardViews.editWorkOrderItem, name="editWorkOrderItem"),
    path("workOrderHistory/", trackingCardViews.workOrderHistory, name="workOrderHistory"),



    path('invoice/api/createInvoice/', views.createInvoiceAPI, name='createInvoiceAPI'),
    path('invoice/api/invoiceAll/', views.invoiceAllAPI, name="invoiceAllAPI"),
    path('invoice/api/itemInvoice/<int:invoice_pk>/', views.itemInvoiceAPI, name="itemInvoiceAPI"),
    path('invoice/api/productsID/<int:id>/', views.productsIDAPI, name="productsIDAPI"),
    path('invoice/api/clientAll/', views.clientsAllAPI, name="clientAllAPI"),
    path('invoice/api/newestProduct/<int:invoice_pk>/', views.newestProductAPI, name="newestProductAPI"),
    path('invoice/api/editInvoiceItem/<int:invoice_pk>/<int:id>/', views.editInvoiceItemAPI, name="editInvoiceItemAPI"),
    path('invoice/api/deleteInvoiceItem/<int:id>/', views.deleteInvoiceItemAPI, name="deleteInvoiceItemAPI"),
    path('invoice/get_invoice_item_count/<int:invoice_id>/', views.get_invoice_item_count, name='get_invoice_item_count'),
    path('invoice/api/invoiceItemNumber/<int:id>/', views.itemInvoiceNumberAPI, name='invoiceItemNumberAPI'),

    path('workOrder/api/createWorkOrder/', trackingCardViews.createWorkOrderAPI, name='createWorkOrderAPI'),
    path('workOrder/api/itemWorkOrder/<int:workOrder_id>/', trackingCardViews.itemWorkOrderAPI, name="itemWorkOrderAPI"),
    path('workOrder/getWorkOrderItemCount/<int:workOrder_id>/', trackingCardViews.getWorkOrderItemCount, name='getWorkOrderItemCount'),
    path('workOrder/api/workOrderItemNumber/<int:id>/', trackingCardViews.itemWorkOrderNumberAPI, name='itemworkOrderNumberAPI'),
    path('workOrder/api/itemWorkOrder/<int:workOrder_id>/', trackingCardViews.itemWorkOrderAPI, name="itemWorkOrderAPI"),
    path('editWorkOrderItemAPI/<int:workOrder_id>/<int:id>/', trackingCardViews.editWorkOrderItemAPI, name="editWorkOrderItemAPI"),
    path('workOrder/api/deleteWorkOrderItem/<int:id>/', trackingCardViews.deleteWorkOrderItemAPI, name="deleteWorkOrderItemAPI"),
    path('workOrder/api/newestProduct/<int:workOrder_id>/', trackingCardViews.newestWorkOrderProductAPI, name="newestWorkOrderProductAPI"),
    path('workOrder/api/workOrderItemOther/<int:id>/', trackingCardViews.workOrderItemOther, name="workOrderItemOther"),
    path('workOrder/api/editWorkOrderItem/<int:workOrder_id>/<int:id>/', trackingCardViews.editWorkOrderItemAPI, name="editWorkOrderItemAPI"),

] 