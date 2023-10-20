from django.shortcuts import render, redirect
from .models import *
from .filters import *
from .forms import *
from .serializers import *
from .urls import *
import requests
import json
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
from django.conf import settings
from django.core.paginator import Paginator, Page
from django.conf import settings
from django.urls import reverse



def index(request):
    context= {}
    return render(request, 'index/index.html', context)

@api_view(['POST'])
def createInvoiceAPI(request):
    if request.method == 'POST':
        serializer = invoiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def invoiceAllAPI(request):
    #http://127.0.0.1:8000/invoice/api/invoiceAll/
    if request.method == "GET":
        invoice = Invoice.objects.all()
        serializer = invoiceSerializer(invoice,many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def clientsAllAPI(request):
    #http://127.0.0.1:8000/invoice/api/clientAll/
    if request.method == "GET":
        client = Client.objects.all()
        serializer = clientSerializer(client,many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['GET','POST'])  
def itemInvoiceAPI(request, invoice_pk):
    if request.method == "GET":
        try:
            items = InvoiceItem.objects.filter(invoice=invoice_pk)
            serializer = invoiceItemSerializer(items, many=True)
            return Response(serializer.data)
        except InvoiceItem.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)  # Return an empty list if no items are found for the given invoice
    if request.method == "POST":
        serializer = invoiceItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Handle other HTTP methods
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    return

@api_view(['GET'])
def productsIDAPI(request, id):
    if request.method == "GET":
        product= Product.objects.get(pk=id)
        serializer = productSerializer(product)
        return JsonResponse(serializer.data, safe=False)
    return

@api_view(['GET'])
def newestProductAPI(request, invoice_pk):
    if request.method == "GET":
        try:
            # Get the specific invoice
            invoice = Invoice.objects.get(invoice_num=invoice_pk)

            # Get the most recent item for the given invoice
            item = InvoiceItem.objects.filter(invoice=invoice).order_by('-created_at')[:1]

            serializer = invoiceItemSerializer(item, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Invoice.DoesNotExist:
            # Handle the case where the specified invoice does not exist
            return JsonResponse({'error': 'Invoice not found'}, status=404)
        
@api_view(['PUT'])
def editInvoiceItemAPI(request, invoice_pk, id):
    try:
        # Try to get the InvoiceItem with the specified ID
        invoice_item = InvoiceItem.objects.get(pk=id)
    except InvoiceItem.DoesNotExist:
        # If the InvoiceItem does not exist, return a 404 Not Found response
        return Response({'detail': 'InvoiceItem not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        # Assuming you have a serializer for your InvoiceItem model
        serializer = invoiceItemSerializer(invoice_item, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
def deleteInvoiceItemAPI(request, id):
    try:
        # Try to get the InvoiceItem with the specified ID
        invoice_item = InvoiceItem.objects.get(pk=id)
    except InvoiceItem.DoesNotExist:
        # If the InvoiceItem does not exist, return a 404 Not Found response
        return Response({'detail': 'InvoiceItem not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        # If the request method is DELETE, delete the InvoiceItem
        invoice_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def createInvoice(request):
    clients = Client.objects.all()
    clientFilter = ClientFilter(request.GET, queryset=clients)
    clients = clientFilter.qs
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            client_id = form.cleaned_data['client'].id 
            invoice_date = form.cleaned_data['invoice_date']

            invoice_date_str = invoice_date.strftime('%Y-%m-%d')


            # Create the API payload using the serialized client data
            api_payload = {
                "client": client_id,
                "invoice_date": invoice_date_str,
                "items": [],
                "status": "Draft"
            }

            # Define the API endpoint URL where you want to send the POST request
            api_url = f'{settings.SITE_URL}/invoice/api/createInvoice/'
            print(api_url)
            print("test")
            print(api_payload)

            try:
                response = requests.post(api_url, json=api_payload)


                if response.status_code == 201:  # Replace with the appropriate status code
                    response_data = json.loads(response.text)
                    invoice_id = response_data.get('invoice_num')
                    print(response_data)
                    # Invoice created successfully
                    return redirect('invoice:addItems', invoice_id)
                else:
                    # Handle API call errors, e.g., show an error message
                    return render(request, 'invoice/createInvoice.html', {'form': form, 'error_message': 'Failed to create invoice'})

            except requests.exceptions.RequestException as e:
                # Handle exceptions such as connection errors
                return HttpResponse('Error: {}'.format(e), status=500)

    else:
        form = InvoiceForm()


    context = {
        'form': form,
        'clients': clients,
        'clientFilter': clientFilter
    }


    return render(request, 'invoice/createInvoice.html', context)

def addItems(request, invoice_id):
    invoice = Invoice.objects.get(pk=invoice_id)
    client = invoice.client
    products = Product.objects.all()
    productType = ProductType.objects.all()
    site_url = settings.SITE_URL

    myFilter = ProductsFilter(request.GET, queryset=products)
    products = myFilter.qs

    paginator = Paginator(products, 10)  # Display 10 invoices per page (you can adjust the number)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    if request.method == 'POST':
        formset = InvoiceItemFormSet(request.POST)
        if formset.is_valid():
            # Create InvoiceItem instances for each valid form
            for form in formset:
                if form.is_valid():
                    product = form.cleaned_data['product']
                    quantity = form.cleaned_data['quantity']
                    unit_price = form.cleaned_data['unit_price']
                    # Create and associate the InvoiceItem with the invoice
                    item = InvoiceItem.objects.create(
                        invoice=invoice,
                        product=product,
                        quantity=quantity,
                    )
                    item.save()

            return redirect('invoice/addItems', invoice_id=invoice_id)  # Redirect back to the same page
    else:
        formset = InvoiceItemFormSet()

    context = {
        'client': client,
        'invoice': invoice,
        'formset': formset,
        'products': products,
        'myFilter': myFilter,
        'site_url': site_url,
    }

    return render(request, 'invoice/addItems.html', context)


def invoiceHistory(request):
    all_invoices = Invoice.objects.order_by('-created_at')  # Ordering by created_at in descending order
    paginator = Paginator(all_invoices, 10)  # Display 10 invoices per page (you can adjust the number)
    page = request.GET.get('page')
    invoices = paginator.get_page(page)
    context = {'invoices': invoices}

    return render(request, 'invoice/invoiceHistory.html', context)

def addProductsClients(request):

    context = {}

    return render(request, 'invoice/addProductsClients.html', context)