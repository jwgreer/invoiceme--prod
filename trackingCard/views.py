from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import io
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from django.http import HttpResponse, JsonResponse
from invoice.models import *
from reportlab.lib import colors
from invoice.filters import ClientFilter, ProductsFilter
from .forms import *
from .serializers import *
from datetime import date, datetime, timedelta
from django.conf import settings
import requests
import json
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, Page
from django.contrib.auth import get_user

@api_view(['GET'])
def newestWorkOrderProductAPI(request, workOrder_id):
    if request.method == "GET":
        try:
            # Get the specific work order
            workOrder = WorkOrders.objects.get(workOrder_num=workOrder_id)

            # Get the most recent item for the given work order
            item = WorkOrderItem.objects.filter(workOrder=workOrder).order_by('-created_at')[:1]

            serializer = workOrderItemSerializer(item, many=True)
            return JsonResponse(serializer.data, safe=False)
        except WorkOrders.DoesNotExist:
            # Handle the case where the specified work order does not exist
            return JsonResponse({'error': 'Work Order not found'}, status=404)

@api_view(['DELETE'])
def deleteWorkOrderItemAPI(request, id):
    try:
        # Try to get the InvoiceItem with the specified ID
        workOrder_item = WorkOrderItem.objects.get(pk=id)
    except WorkOrderItem.DoesNotExist:
        # If the InvoiceItem does not exist, return a 404 Not Found response
        return Response({'detail': 'Work Order not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        # If the request method is DELETE, delete the InvoiceItem
        workOrder_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PUT'])
def editWorkOrderItemAPI(request, workOrder_id, id):
    try:
        # Try to get the InvoiceItem with the specified ID
        workOrder_item = WorkOrderItem.objects.get(pk=id)
    except WorkOrderItem.DoesNotExist:
        # If the InvoiceItem does not exist, return a 404 Not Found response
        return Response({'detail': 'Work Order Item not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        # Assuming you have a serializer for your InvoiceItem model
        serializer = workOrderItemSerializer(workOrder_item, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'POST'])
def itemWorkOrderAPI(request, workOrder_id):
    if request.method == "GET":
        try:
            items = WorkOrderItem.objects.filter(workOrder=workOrder_id)
            
            #serializer = workOrderItemSerializer(items, many=True)
            #return Response(serializer.data)
            
            raw_item_list = []  # Create an empty list to store raw item data

            for item in items:
                product_type = item.product.product_type.name

                if product_type == "Other":
                    raw_item_data = {
                        'id': item.id,
                        'product_name': item.custom_product_name,
                        'description': item.custom_product_description,
                        'quantity': item.quantity,
                        'product_id': item.product.id,
                        'product_type': product_type,
                        'number': item.number
                        # Add other fields you want to include
                    }
                    raw_item_list.append(raw_item_data)
                else:
                    raw_item_data = {
                        'id': item.id,
                        'product_name': item.product.name,
                        'description': item.description,
                        'quantity': item.quantity,
                        'product_id': item.product.id,
                        'product_type': product_type,
                        'number': item.number
                        # Add other fields you want to include
                    }
                    raw_item_list.append(raw_item_data)

            return Response(raw_item_list, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)  # Return an empty list with a 200 OK status

    elif request.method == "POST":
        serializer = workOrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Handle other HTTP methods
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['PUT'])
def itemWorkOrderNumberAPI(request, id):
    try:
        item = WorkOrderItem.objects.get(pk=id)  # Use get() to retrieve a single instance
    except WorkOrderItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    
    if request.method == "PUT":
        serializer = workOrderItemNumberSerializer(item, data=request.data)  # Pass request data to the serializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@api_view(['GET']) 
def getWorkOrderItemCount(request, workOrder_id):
    count = WorkOrderItem.objects.filter(workOrder=workOrder_id).count()
    data = {'count': count}
    return JsonResponse(data)

@api_view(['POST'])
def createWorkOrderAPI(request):
    if request.method == 'POST':
        serializer = workOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
def editWorkOrderItemAPI(request, workOrder_id, id):
    try:
        # Try to get the InvoiceItem with the specified ID
        workOrder_item = WorkOrderItem.objects.get(pk=id)
    except InvoiceItem.DoesNotExist:
        # If the InvoiceItem does not exist, return a 404 Not Found response
        return Response({'detail': 'Work Order Item not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        # Assuming you have a serializer for your InvoiceItem model
        serializer = workOrderItemSerializer(workOrder_item, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@login_required(login_url='invoice:loginPage')
def workOrderHistory(request):
    all_workOrders = WorkOrders.objects.order_by('-created_at')  # Ordering by created_at in descending order
    paginator = Paginator(all_workOrders, 10)  # Display 10 invoices per page (you can adjust the number)
    page = request.GET.get('page')
    workOrders = paginator.get_page(page)
    context = {'workOrders': workOrders}

    return render(request, 'tracking/workOrderHistory.html', context)

@login_required
def editWorkOrderItem(request, workOrder_id, id):
    workOrder_id = WorkOrders.objects.get(pk=workOrder_id)
    item_id = WorkOrderItem.objects.get(pk=id)
    client = workOrder_id.client
    products = Product.objects.all()
    site_url = settings.SITE_URL

    context = {
        'invoice_id': workOrder_id,
        'itemId': item_id,
        'products': products,
        'site_url': site_url,
    }
    return render(request, 'invoice/editItemForm.html', context)

@login_required(login_url='invoice:loginPage')
def createWorkOrder(request):
    current_user = request.user
    print(current_user.username)
    clients = Client.objects.all()
    clientFilter = ClientFilter(request.GET, queryset=clients)
    clients = clientFilter.qs
    if request.method == 'POST':
        form = WorkOrderForm(request.POST)
        if form.is_valid():
            client_id = form.cleaned_data['client'].id
            print(client_id)

            today = date.today()

            # Format the date as a string in 'YYYY-MM-DD' format
            invoice_date_str = today.strftime('%Y-%m-%d')




            # Create the API payload using the serialized client data
            api_payload = {
                "client": client_id,
                "workOrder_date": invoice_date_str,
                "items": [],
                "status": "Waiting_on_Assignment",
                "created_by": current_user.username
            }

            # Define the API endpoint URL where you want to send the POST request
            api_url = f'{settings.SITE_URL}/workOrder/api/createWorkOrder/'
            print(api_url)
            print(api_payload)

            try:
                response = requests.post(api_url, json=api_payload)


                if response.status_code == 201:  # Replace with the appropriate status code
                    response_data = json.loads(response.text)
                    print(response_data)
                    workOrder_id = response_data.get('workOrder_num')
                    print(response_data)
                    print(workOrder_id)
                    # Invoice created successfully
                    return redirect('invoice:workOrderEnrichmentForm', workOrder_id)
                else:
                    # Handle API call errors, e.g., show an error message
                    return render(request, 'tracking/createWorkOrder.html', {'form': form, 'error_message': 'Failed to create Work Order'})

            except requests.exceptions.RequestException as e:
                # Handle exceptions such as connection errors
                return HttpResponse('Error: {}'.format(e), status=500)

    else:
        form = WorkOrderForm()


    context = {
        'form': form,
        'clients': clients,
        'clientFilter': clientFilter,
        'user': current_user
    }


    return render(request, 'tracking/createWorkOrder.html', context)


def workOrderEnrichmentForm(request, workOrder_id):
    form = WorkOrderEnrichmentForm(request.POST)

    if request.method == 'POST':
        
        if form.is_valid():
            try:
                workOrder = WorkOrders.objects.get(pk=workOrder_id)
                rush = form.cleaned_data['is_rush']
                return_by = form.cleaned_data['return_by']
                quote_required = form.cleaned_data['quote_required']
                special_instructions = form.cleaned_data['specialInstructions']
                workOrder.is_rush = rush
                workOrder.return_by = return_by
                workOrder.quote_required = quote_required
                workOrder.specialInstructions = special_instructions
                workOrder.save()
                messages.success(request, "Company info has been updated." )
                return redirect('invoice:addItemsWorkOrder', workOrder_id)
            except Exception as e:
                messages.error(request, "Something went wrong.")
                print(e)
                print("End of Exception  ==========================")
    context = {
        'workOrder_id': workOrder_id,
        'form': form

    }   

    return render(request, 'tracking/workOrderEnrichmentForm.html', context)


def customWorkOrderItem(request, workOrder_id):
    count = WorkOrderItem.objects.filter(workOrder=workOrder_id).count()
    if count == 0:
        count = 1
    else:
        count += 1
    productType = ProductType.objects.get(name="Other")


    if request.method == 'POST':
        form = WorkOrderItemOtherForm(request.POST)
        if form.is_valid():
            form.instance.created_by = request.user
            form.save()
            # Process the form data and save it to the database
            return redirect('invoice:addItemsWorkOrder', workOrder_id)  # Redirect to a success page
    else:
        initial_data = {
            'workOrder': workOrder_id,
            'number': count,
            'product': productType.id
        }
        form = WorkOrderItemOtherForm(initial=initial_data)
    
    return render(request, 'tracking/customWorkOrderItem.html', {'form': form})




@login_required(login_url='invoice:loginPage')
def addItemsWorkOrder(request, workOrder_id):
    workOrder_id = WorkOrders.objects.get(pk=workOrder_id)
    client = workOrder_id.client
    products = Product.objects.all()
    products = products.exclude(name="Other")
    productType = ProductType.objects.all()
    productType = productType.exclude(name="Other")
    site_url = settings.SITE_URL

    myFilter = ProductsFilter(request.GET, queryset=products)
    products = myFilter.qs

    paginator = Paginator(products, 10)  # Display 10 invoices per page (you can adjust the number)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    if request.method == 'POST':
        formset = WorkOrderItemFormSet(request.POST)
        if formset.is_valid():
            # Create InvoiceItem instances for each valid form
            for form in formset:
                if form.is_valid():
                    product = form.cleaned_data['product']
                    quantity = form.cleaned_data['quantity']
                    unit_price = form.cleaned_data['unit_price']
                    # Create and associate the InvoiceItem with the invoice
                    item = WorkOrderItem.objects.create(
                        workorder=workOrder_id,
                        product=product,
                    )
                    item.save()

            return redirect('invoice:addTracking', workOrder_id)  # Redirect back to the same page
    else:
        formset = WorkOrderItemFormSet()

    context = {
        'client': client,
        'workOrder_id': workOrder_id,
        'formset': formset,
        'products': products,
        'myFilter': myFilter,
        'site_url': site_url,
    }

    return render(request, 'tracking/addItemsWorkOrder.html', context)

@api_view(['GET'])
def workOrderItemOther(request, id):
    if request.method == "GET":
        item= WorkOrderItem.objects.get(pk=id)
        serializer = workOrderItemOtherNameSerializer(item)
        return JsonResponse(serializer.data, safe=False)
    return


@login_required(login_url='invoice:loginPage')
def shopWorkDashboard(request):
    context = {}
    return render(request, 'tracking/shopWorkDashboard.html', context)


@login_required(login_url='invoice:loginPage')
def pdfCustomerTracking(request, workOrder_id):
    workOrder = WorkOrders.objects.get(pk=workOrder_id)
    contacts = ClientContact.objects.get(client = workOrder.client)
    primaryContact = ClientContact.objects.get(client=workOrder.client, status='Primary')
    primaryContact = f"{primaryContact.first_name} {primaryContact.last_name}"

    try:
        user = User.objects.get(username=workOrder.created_by)
        created_by = f"{user.first_name} {user.last_name}"

    except User.DoesNotExist:
        # Handle the case when the user with the given username doesn't exist
        created_by = ""
    

    items = WorkOrderItem.objects.filter(workOrder=workOrder)



    buffer = io.BytesIO()

    p = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
    p.translate(1*inch, 1*inch)
   
   # build the container
    p.line(-0.8*inch, 0.0*inch,7.3*inch, 0.0*inch)# bottom horizontal line total
    p.line(-0.8*inch, 3.5*inch,7.3*inch, 3.5*inch)# top horizontal line total
    p.line(-0.8*inch,4.5*inch,-0.8*inch,0.0*inch)# right first vertical line
    p.line(7.3*inch,4.5*inch,7.3*inch,0.0*inch)# left second vertical line


    p.line(3.8*inch,1.5*inch,3.8*inch,0.0*inch)# right first vertical line
    p.line(-0.8*inch, 1.5*inch,7.3*inch, 1.5*inch)# bottom horizontal line total

    fill_color = (0.2, 0.4, 0.6)
    p.setFillColor(fill_color)
    p.circle(2.8*inch, 0.6*inch, 0.5*inch, fill=1)

    fill_color = colors.black
    p.setFillColor(fill_color)


    # signature box

    p.line(-.6*inch,2.0*inch,2.5*inch,2.0*inch)# right first vertical line
    p.line(-.6*inch,2.6*inch,2.5*inch,2.6*inch)# right first vertical line
    p.line(-.6*inch,3.2*inch,2.5*inch,3.2*inch)# right first vertical line
    p.line(-0.6*inch,3.2*inch,-0.6*inch,2.0*inch)# right first vertical line
    p.line(2.5*inch,3.2*inch,2.5*inch,2.0*inch)# right first vertical line


    p.line(3.0*inch,2.0*inch,7.1*inch,2.0*inch)# right first vertical line
    p.line(3.0*inch,3.2*inch,7.1*inch,3.2*inch)# right first vertical line
    p.line(3.0*inch,3.2*inch,3.0*inch,2.0*inch)# right first vertical line
    p.line(7.1*inch,3.2*inch,7.1*inch,2.0*inch)# right first vertical line

    
    p.line(-0.8*inch, 4.1*inch,7.3*inch, 4.1*inch)# bottom horizontal line total
    p.line(-.4*inch,4.1*inch,-.4*inch,4.5*inch)# second 
    p.line(.2*inch,4.1*inch,.2*inch,4.5*inch)# right first vertical line
    p.line(1.5*inch,4.1*inch,1.5*inch,4.5*inch)# right first vertical line
    p.line(6.3*inch,4.1*inch,6.3*inch,4.5*inch)# right first vertical line
    p.line(-0.8*inch, 4.5*inch,7.3*inch, 4.5*inch)# bottom horizontal line total
    
    
    p.line(7.0*inch,0.4*inch,7.0*inch,1.3*inch)# 5
    p.line(5.5*inch,0.4*inch,5.5*inch,1.3*inch)# 5
    p.line(5.5*inch,.4*inch,7.0*inch,0.4*inch)# right first vertical line
    p.line(5.5*inch,1.3*inch,7.0*inch,1.3*inch)# right first vertical line

    p.line(5.5*inch,.7*inch,7.0*inch,.7*inch)# right first vertical line

    p.line(5.5*inch,1.0*inch,7.0*inch,1.0*inch)# right first vertical line
    
    # today date
    p.line(5.7*inch,3.6*inch,5.7*inch,4.0*inch)#  first vertical
    p.line(7.0*inch,3.6*inch,7.0*inch,4.0*inch)# second vertical

    p.line(5.7*inch, 3.6*inch,7.0*inch, 3.6*inch)# top line
    p.line(5.7*inch, 4.0*inch,7.0*inch, 4.0*inch)# bottom horizontal line total


    p.line(2.2*inch,3.6*inch,2.2*inch,4.0*inch)#  first vertical
    p.line(3.5*inch,3.6*inch,3.5*inch,4.0*inch)# second vertical

    p.line(2.2*inch, 3.6*inch,3.5*inch, 3.6*inch)# top line
    p.line(2.2*inch, 4.0*inch,3.5*inch, 4.0*inch)# bottom horizontal line total
    
    


 




    p.setFont("Helvetica-Bold", 15)
    p.drawString(1.0*inch, -.3*inch, "Customer Items to Repair Center Tracking")
    p.drawString(-.6*inch, .3*inch, "1. Customer:")
    p.drawString(-.5*inch, .7*inch, workOrder.client.name)
    p.drawString(-.5*inch, 1.0*inch, workOrder.client.address)
    p.drawString(4.0*inch, .3*inch, "2. Reference Information")
    p.drawString(-.6*inch, 1.8*inch, "3. Signatures")
    p.drawString(3.0*inch, 1.8*inch, "4. Special Instructions")
    p.drawString(-.6*inch, 3.8*inch, "5. Items")
    p.drawString(.6*inch, 3.8*inch, "6. RETURN BY")
    p.drawString(3.8*inch, 3.8*inch, "7. TODAYS DATE")
    p.drawString(-0.2*inch, 2.5*inch, primaryContact)
    p.drawString(-0.2*inch, 3.1*inch, created_by)


    p.setFont("Helvetica", 10)
    p.drawString(4.0*inch, .6*inch, "P.O OR DISPO #")
    p.drawString(4.0*inch, .9*inch, "RUSH THIS ORDER? ")
    if workOrder.is_rush == True:
        p.drawString(6.1*inch, .9*inch, 'YES')
    else:
        p.drawString(6.1*inch, .9*inch, 'NO')

    p.drawString(4.0*inch, 1.2*inch, "Quote Required?")
    if workOrder.quote_required == True:
        p.drawString(6.1*inch, 1.2*inch, "YES")
    else:
        p.drawString(6.1*inch, 1.2*inch, "NO")
    p.drawString(5.8*inch, -.3*inch, "Tracking ID #: ")
    p.drawString(6.9*inch, -.3*inch, str(workOrder.pk))
    p.drawString(-0.3*inch, -.3*inch, "Simnar Logo")
    p.drawString(2.4*inch, 1.3*inch, "Group Decal")

    p.drawString(-.50*inch, 2.2*inch, "Customer:")
    
    p.drawString(-.5*inch, 2.8*inch, "Simnar Rep:")
    p.setFont("Helvetica", 12)
    p.drawString(-.3*inch, 4.35*inch, "QTY")
    p.drawString(.3*inch, 4.35*inch, "MFG #, Label")
    p.drawString(1.6*inch, 4.35*inch, "Description of Item")
    p.drawString(6.45*inch, 4.35*inch, "STATUS")
    # todays date
    dt = date.today().strftime('%Y-%m-%d')
    p.drawString(5.9*inch,3.85*inch,dt)
      # Format the date as a string
    return_by_date = workOrder.return_by

    if return_by_date == None:
        return_by_date = ""
    else:
        return_by_date = workOrder.return_by.strftime('%Y-%m-%d')

    p.drawString(2.4 * inch, 3.85 * inch, return_by_date)

    sp = workOrder.specialInstructions
    part1 = sp[:50]
    part2 = sp[50:100]
    part3 = sp[100:150]
    part4 = sp[150:200]
    part5 = sp[200:250]

    p.drawString(3.1*inch, 2.2*inch, part1)
    p.drawString(3.1*inch, 2.40*inch, part2)
    p.drawString(3.1*inch, 2.60*inch, part3)
    p.drawString(3.1*inch, 2.80*inch, part4)
    p.drawString(3.1*inch, 3.0*inch, part5)




    arr = [1,2,3,4, 5, 6,5,4,3,3]
    count = 0
    x = 4.5
    x1 = 4.9

    x3 = 4.75
    for i in items:

        if i.product.id  == 2:
            description = i.custom_product_description
            print("other")
            print(i.custom_product_description)
            print("other")
            name = i.custom_product_name
            print()
        else: 
            description = i.description
            name = i.product.name

        if description is None:
            description = ""
            name =""


        
        
        p.drawString(-.65*inch, x3*inch, i.number)
        p.drawString(-.2*inch, x3*inch, str(i.quantity))
        p.drawString(.25*inch, x3*inch, name)
        p.drawString(1.55*inch, x3*inch, description)
        p.drawString(6.5*inch, x3*inch, "BUSTED")


        p.line(-0.8*inch, x1*inch,7.3*inch, x1*inch)# bottom 
        p.line(-0.8*inch,x*inch,-0.8*inch,x1*inch)# 1
        p.line(-.4*inch,x*inch,-.4*inch,x1*inch)# 2 
        p.line(.2*inch,x*inch,.2*inch,x1*inch)# 3
        p.line(1.5*inch,x*inch,1.5*inch,x1*inch)# 4
        p.line(6.3*inch,x*inch,6.3*inch,x1*inch)# 5
        p.line(7.3*inch,x*inch,7.3*inch,x1*inch)# 6v

        x = x +.4
        x1 = x1 +.4
        x3 = x3+.4
   

        if count == 12:
            p.showPage() 
            p.translate(1*inch, 1*inch) # Start a new page every time a multiple of 3 is reached

            x = -0.6
            x1 = 2.4


        count +=1


    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="invoice.pdf"'

    return response



@login_required(login_url='invoice:loginPage')
def pdfTracker(request, workOrder_id):
    workOrder = WorkOrders.objects.get(pk=workOrder_id)
    items = WorkOrderItem.objects.filter(workOrder=workOrder)
    item_arr = []
    item_number_arr = []
    counter = 0

    for item in items:
        quantity = 1
        i = 0
        if item.quantity > 1:
            quantity = item.quantity

        while i < quantity:
            product = item.product
            item_arr.append(item.product.name)
            item_number_arr.append(item.number)

            i +=1



    buffer = io.BytesIO()

    # Create the PDF object with landscape orientation, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=landscape(letter), bottomup=0)

    x = -0.6
    x1 = 2.4
    x3 = 1.4
    x4 = 1.5

    x2 = -.5

    p.translate(1*inch, 1*inch)  # Adjust as needed for your content placement

    for i in item_arr:
        # Your content and drawing instructions go here

        p.line(x*inch, -0.5*inch, x1*inch, -0.5*inch)  # Top horizontal line total
        p.line(x*inch, 7.0*inch, x*inch, -0.5*inch)  # Right first vertical line
        p.line(x1*inch, 7.0*inch, x1*inch, -0.5*inch)  # Left vertical line
        p.line(x*inch, 7.0*inch, x1*inch, 7.0*inch)  # Bottom horizontal line total

        p.drawString(x2*inch, .0*inch, "Instrument Tracking Card")
        p.drawString(x2*inch, .5*inch, "Client Name: " + workOrder.client.name)
        p.drawString(x2*inch, 1.0*inch, "Address: "+ workOrder.client.address)
        p.drawString(x2*inch, 1.5*inch, "Contact: John Doe")
        p.drawString(x2*inch, 2.0*inch, "Instrument: "+ str(item_arr[counter]))
        p.drawString(x2*inch, 2.5*inch, "Repair Notes: " )
        p.drawString(x2*inch, 3.0*inch, "The thing is busted and we dont " )
        p.drawString(x2*inch, 3.3*inch, "know how we are going to fix it " )
        p.drawString(x2*inch, 3.6*inch, "but one thing we know is it will " )
        p.drawString(x2*inch, 3.9*inch, "be expensive." )
        p.drawString(x2*inch, 6.0*inch, "Thank You For Your Service!")
        p.drawString(x2*inch, 6.5*inch, "Simnar Surgical")
        o, v, width, height = x3*inch, 6.2*inch, .75*inch, .75*inch

        # Set the fill color for the square
        fill_color = colors.red  # You can use other colors like colors.blue, colors.green, etc.

        # Draw the square and fill it with the specified color
        p.setFillColor(fill_color)
        p.rect(o, v, width, height, fill=1)

        fill_color = colors.black
        p.setFillColor(fill_color)
        p.setFont("Times-Bold", 30)
        p.drawString(x4*inch, 6.7*inch, str(item_number_arr[counter]))
        p.setFont("Helvetica", 12)
        



        



        x = x + 3.6
        x1 = x1 + 3.6
        x2 = x2 + 3.6
        x3 = x3 + 3.6
        x4 = x4 + 3.6

        if (counter + 1) % 3 == 0 and (counter + 1) < len(item_arr):
            
            p.showPage() 
            p.translate(1*inch, 1*inch) # Start a new page every time a multiple of 3 is reached

            x = -0.6
            x1 = 2.4
            x2 = -.5
            x3 = 1.4
            x4 = 1.5

        counter +=1
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="invoice.pdf"'

    return response

