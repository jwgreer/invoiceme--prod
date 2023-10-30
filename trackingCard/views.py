from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required
import io
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.graphics import renderSVG
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib.utils import ImageReader
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from invoice.models import *
from invoice.filters import ClientFilter, ProductsFilter
from .forms import *
from .serializers import *
from datetime import date, datetime, timedelta
from django.conf import settings
import requests
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, Page
from django.forms import inlineformset_factory
from PIL import Image
import os
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import get_object_or_404



@api_view(['POST'])
def addItemTestAPI(request):
    if request.method == "POST":
        try:
            d = request.data.get('data', {})
            quantity = int(d["quantity"]) 
            workOrder_id = d.get('workOrder', None)  # Use get with a default value to avoid KeyError
        except (KeyError, ValueError) as e:
            # Handle the exception by returning an error response
            error_message = "Invalid request data: " + str(e)
            return Response("PLEASE ENTER A VALID NUMBER", status=status.HTTP_400_BAD_REQUEST)

        if d['product'] in ["3", "4"]:
            print("test")
            i = 0
            
            if quantity > 1:
                created_items = []
                while i < quantity:
                    # Create a new dictionary to avoid modifying the original data
                    d['quantity'] = "1"
                    d['number'] = str(WorkOrderItem.objects.filter(workOrder=workOrder_id).count() + 1)
                    serializer = workOrderItemSerializer(data=d)

                    if serializer.is_valid():
                        serializer.save()
                        created_items.append(serializer.data)
                        print(i)
                        i += 1
                return Response(created_items, status=status.HTTP_201_CREATED)
            
            # Quantity is not greater than 1, handle it as a single item
            serializer = workOrderItemSerializer(data=d)
            d['number'] = str(WorkOrderItem.objects.filter(workOrder=workOrder_id).count() + 1)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            
            d['number'] = str(WorkOrderItem.objects.filter(workOrder=workOrder_id).count() + 1)
            print(d['issue'])
            # If the product is not "3" or "4", handle it as a single item
            serializer = workOrderItemSerializer(data=d)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def workOrderEnrichment(request):

    if request.method == 'POST':
        try:
            data = request.data
            type = data.get('type', '')
            value = data.get('value', '')
            id = data.get('workOrder_id','')
            workOrder = WorkOrders.objects.get(pk=id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        print(data)
        
        
        if type == 'is_rush':
            try:
                workOrder.is_rush = value
                workOrder.status = 'Rush'
                workOrder.save()
                return Response(status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif type == "return_by":
            try:
                workOrder.return_by = value

                workOrder.save()
                return Response(status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif type == "quote_required":
            try:
                workOrder.quote_required = value
                workOrder.save()
                return Response(status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
        elif type == "specialInstructions":
            try:
                workOrder.specialInstructions = value
                workOrder.save()
                return Response(status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        
            
    return Response(status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def workOrderViewAPI(request):
    
    if request.method == 'POST':
        
        data = request.data
        type = data.get('type', '')
        value = data.get('value', '')
        
        if value is None:
            return
        id = data.get('id', '')
        try:
            item = WorkOrderItem.objects.get(pk=id)
        except: 
            pass

        print(type)
        if type == 'technician':
            if value == 'none':
                print("none")
                item.technician = None
                item.save()
                return Response(status=status.HTTP_200_OK)
            user = User.objects.get(id=value)
            item = WorkOrderItem.objects.get(pk=id)
            item.technician = user
            item.status = 'Checked_Out'
            item.save()
            return Response(status=status.HTTP_200_OK)
        elif type =='status':
            if value == 'Needs_QC':
                item.qc = 'WAITING_QC'
                item.status = value
                item.save()
                return Response(status=status.HTTP_200_OK)
            item.status = value
            item.save()
            return Response(status=status.HTTP_200_OK)
        elif type == 'qc':
            if value ==  'QC_PASS':
                item.status = value
                item.qc = value
                item.save()
                return Response(status=status.HTTP_200_OK)
            elif value == 'QC_FAIL':
                item.status =value
                item.qc = value
                item.save()
                return Response(status=status.HTTP_200_OK)

            item.qc = value
            item.save()
            return Response(status=status.HTTP_200_OK)
        elif type == 'workOrderStatus':
            try:
                workOrder = WorkOrders.objects.get(pk=id)
                workOrder.status = value
                workOrder.save()
                return Response(status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)

        return Response({'message': 'Data received and processed successfully'})

@api_view(['PUT'])
def workOrderColorAPI(request, workOrder_id):
    try:
        # Retrieve the work order by its ID
        work_order = WorkOrders.objects.get(pk=workOrder_id)
    except WorkOrders.DoesNotExist:
        return Response({'message': 'Work order not found.'}, status=status.HTTP_404_NOT_FOUND)
    try:
        # Retrieve the second most recent work order
        work_order2 = WorkOrders.objects.all().order_by('-created_at')[1]
    except:
        pass
   
    try:
        serializer = workOrderColorSerializer(work_order2)
        color = work_order2.color
    except:
        color = None
        pass


    # 35 total colors
    color_list = [
        "red","black", "green", "blue", "yellow", "orange","aqua", "pink", "brown", "beige",
        "bisque", "chocolate", "darkblue", "darkred","dodgerblue", "darkgreen", "darkorange",
        "darkgrey", "gold", "grey", "hotpink", "indigo", "lawngreen",
         "lightblue","burlywood","crimson", "magenta", "maroon", "navy", "olive", "salmon",
        "silver", "tan", "teal", "violet"
    ]

    if color is None:
        color = color_list[0]
        work_order.color = color
        work_order.save()
        serializer = workOrderColorSerializer(work_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif color not in color_list:
        color = "red"  # Use the first color if there's no second recent work order
    else:
        # Find the index of the current color in the list
        current_color_index = color_list.index(color)
        
        # Determine the next index by adding 1 and taking the remainder to cycle
        next_color_index = (current_color_index + 1) % len(color_list)
        
        # Get the next color from the list
        color = color_list[next_color_index]

    try:
        work_order.color = color
        work_order.save()
        serializer = workOrderColorSerializer(work_order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print("Error:", str(e))
        return Response({'message': 'Error updating work order.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
def deleteWorkOrderItemAPI(request):
    try:
        data = request.data
        print(data)
        workOrder_id = data.get('workOrder_id', '')
        id = data.get('id', '')
        item = WorkOrderItem.objects.get(pk=id)
        
    except WorkOrderItem.DoesNotExist:
        return Response({'detail': 'Work Order Item not found'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': f'Error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        try:
            item.delete()
            items = WorkOrderItem.objects.filter(workOrder=workOrder_id)
            counter = 1
            for i in items:
                i.number = counter
                i.save()
                counter += 1
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': f'Unable to delete: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)



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
            
            raw_item_list = []

            for item in items:
                product_type = item.product.product_type.name

                if product_type == "Other":
                    product_name = item.custom_product_name
                    description = item.custom_product_description
                else:
                    product_name = item.product.name
                    description = item.description

                raw_item_data = {
                    'id': item.id,
                    'product_name': product_name,
                    'description': description,
                    'quantity': item.quantity,
                    'product_id': item.product.id,
                    'product_type': product_type,
                    'number': item.number
                    # Add other fields you want to include
                }
                raw_item_list.append(raw_item_data)

            return Response(raw_item_list, status=status.HTTP_200_OK)
        except WorkOrderItem.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)

    elif request.method == "POST":
        d = request.data
        print(d)
        i = 0
        quantity = int(d["quantity"])  # Use get with a default value to avoid KeyError

        if d['product'] in ["3", "4"]:
            
            if quantity > 1:
                created_items = []
                while i < quantity:
                    # Create a new dictionary to avoid modifying the original data
                    d['quantity'] = "1"
                    d['number'] = str(WorkOrderItem.objects.filter(workOrder=workOrder_id).count() + 1)
                    serializer = workOrderItemSerializer(data=d)

                    if serializer.is_valid():
                        serializer.save()
                        created_items.append(serializer.data)
                        print(i)
                        i += 1
                return Response(created_items, status=status.HTTP_201_CREATED)
            
            # Quantity is not greater than 1, handle it as a single item
            serializer = workOrderItemSerializer(data=d)
            d['number'] = str(WorkOrderItem.objects.filter(workOrder=workOrder_id).count() + 1)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            
            d['number'] = str(WorkOrderItem.objects.filter(workOrder=workOrder_id).count() + 1)
            print(d['issue'])
            # If the product is not "3" or "4", handle it as a single item
            serializer = workOrderItemSerializer(data=d)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    return render(request, 'tracking/editWorkOrderItemForm.html', context)

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
                    workOrder_id = response_data.get('workOrder_num')
                    print(response_data)
                    
                    api_url = f'{settings.SITE_URL}/workOrder/api/addColor/{workOrder_id}/'
                    api_payload = {"id": workOrder_id}
                    response = requests.put(api_url, json=api_payload)

                    print(response_data)
                    print(workOrder_id)
                    # Invoice created successfully
                    return redirect('invoice:addItemsWorkOrder', workOrder_id)
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

@login_required(login_url='invoice:loginPage')
def deleteWorkOrderItem(request,workOrder_id, id ):
    form = WorkOrderItemDelete(request.DELETE)
    if request.method == 'DELETE':
        if form.is_valid():
            form.save()
            return redirect('invoice:addItemsWorkOrder', workOrder_id)


@login_required(login_url='invoice:loginPage')
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

    
    workOrder = WorkOrders.objects.get(pk=workOrder_id)

    if (not request.user.groups.filter(name='admin')) and workOrder.status != "Waiting_on_Assignment":
        s = workOrder.status
        return HttpResponseForbidden(f"The current status is '{s}'. Only admin can view this page.")
    
    deleteForm = WorkOrderItemDelete(request.POST)
    workOrderItems = WorkOrderItem.objects.filter(workOrder=workOrder_id)
    workOrder_id = WorkOrders.objects.get(pk=workOrder_id)
    client = workOrder_id.client
    products = Product.objects.all()
    products = products.exclude(name="Other")
    productType = ProductType.objects.all()
    productType = productType.exclude(name="Other")
    site_url = settings.SITE_URL

    myFilter = ProductsFilter(request.GET, queryset=products)
    products = myFilter.qs

    paginator = Paginator(products, 5)  # Display 10 invoices per page (you can adjust the number)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    otherForm = WorkOrderItemOtherForm(request.POST)
    initial_return_by = (datetime.now() + timedelta(days=7)).date().strftime('%Y-%m-%d')
    print(workOrder.return_by)
    if workOrder.return_by is None:
        initial_return_by = (datetime.now() + timedelta(days=7)).date().strftime('%Y-%m-%d')
        workOrder.return_by = initial_return_by
        workOrder.save()
    else:
        initial_return_by = workOrder.return_by
    initial = {
        'is_rush': workOrder.is_rush,
        'quote_required': workOrder.quote_required,
        'specialInstructions': workOrder.specialInstructions,
        'return_by': initial_return_by
    }

    workOrderForm = WorkOrderEnrichmentForm(request.POST or None,initial=initial)

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
        'otherForm': otherForm,
        'workOrderItems': workOrderItems,
        'workOrder': workOrder,
        'workOrderForm': workOrderForm,
        'initial_return_by': initial_return_by
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

    latest_workOrders = WorkOrders.objects.order_by('-created_at')[:5]
    rush_workOrders = WorkOrders.objects.filter(status='Rush')
    instruments_waiting_on_parts = WorkOrderItem.objects.filter(status="Parts_On_Order")

    context = {
        'latest_workOrders': latest_workOrders,
        'instruments_waiting_on_parts': instruments_waiting_on_parts,
        'rush_workOrders': rush_workOrders
    }

    return render(request, 'tracking/shopWorkDashboard.html', context)
@login_required(login_url='invoice:loginPage')
def workOrderView(request, workOrder):
    workOrder_ = WorkOrders.objects.get(pk=workOrder)
    workOrderItems = WorkOrderItem.objects.filter(workOrder=workOrder)
    choices = [choice[1] for choice in WorkOrders.STATUS_CHOICES]
    site_url = settings.SITE_URL

    initial_list = []
    for i in workOrderItems:
        initial = {
            'status': i.status,
            'qc': i.qc,
            'technician': i.technician.pk if i.technician else None,
            'item_id': i.pk
        }
        initial_list.append(initial)

    form = WorkOrderViewForm(request.POST or None)
    

    if request.method == 'POST':
        formset = WorkOrderViewFormSet(request.POST)  
        if formset.is_valid():
            for form in formset:
                if form.is_valid():
                    status = form.cleaned_data['status']
                    qc = form.cleaned_data['qc']
                    technician = form.cleaned_data['technician']
                    
                    # Retrieve the existing WorkOrderItem instance based on a unique identifier
                    item_id = form.cleaned_data['item_id']
                    print(item_id)  # Replace 'item_id' with the actual field name
                    item = WorkOrderItem.objects.get(pk=item_id)
                    print(item_id)
                    
                    # Update the fields and save the item
                    item.status = status
                    item.qc = qc
                    item.technician = technician
                    item.save()
                    
                    
        else:
            print("invalid")
    else:
        formset = WorkOrderViewFormSet()

    context = {
        'workOrder': workOrder_,
        'workOrderItems': workOrderItems,
        'workOrder_id': workOrder,
        'formset': formset,
        'form': form,
        'site_url': site_url,
        'choices': choices
    }

    return render(request, 'tracking/workOrderView.html', context)

@login_required(login_url='invoice:loginPage')
def signature_page(request, workOrder_id):
    workOrder_ = WorkOrders.objects.get(pk=workOrder_id)
    context = {
        'workOrder': workOrder_,
        'workOrder_id': workOrder_id
    }
    return render(request, 'tracking/draw_signature.html', context)

@api_view(['POST'])
def signatureAPI(request):
    try:
        print(request.data)
        image = request.data.get('image', '')  # Get the image data from the request
        workOrder_id = int(request.data.get('workOrder_id',''))


    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    if request.method == "POST":
        try:
            # Get the WorkOrder instance (replace this with your logic to fetch the correct WorkOrder)
            work_order = WorkOrders.objects.get(pk=workOrder_id)  # Replace with the actual ID or lookup criteria


            # Create and save the Signature instance with the associated WorkOrder
            signature = Signature(image=image, workOrder=work_order)
            signature.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@xframe_options_exempt
@login_required(login_url='invoice:loginPage')
def pdfCustomerTracking(request, workOrder_id):
    workOrder = WorkOrders.objects.get(pk=workOrder_id)
    c = workOrder.color

    if c is None or c == "":
        c = "red"
    
    logo = 'static/img/simnarLogo.png'


    showpg = False

    try:
        user = User.objects.get(username=workOrder.created_by)
        created_by = f"{user.first_name} {user.last_name}"

    except User.DoesNotExist:
        # Handle the case when the user with the given username doesn't exist
        created_by = ""
    

    try:
        signature = Signature.objects.filter(workOrder=workOrder_id).latest('created_at')
    except:
        signature = None

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
      # Change the index to select the desired color from the list
    
    p.setFillColor(c)
    p.circle(2.8 * inch, 0.6 * inch, 0.5 * inch, fill=1)

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
    if signature:
        signature_image_path = signature.image.path
        p.saveState()
        p.scale(1, -1)  
        p.drawImage(signature_image_path, 0.3 *inch,-2.6*inch, width=125, height=45, mask='auto')
        p.restoreState()
    else:
        pass



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
    p.saveState()
    p.scale(1,-1)
    p.drawImage(logo, -.7 * inch, .1 * inch, width=100, height=50, mask='auto')
    p.restoreState()
    p.drawString(2.45*inch, 1.25*inch, "Group Decal")

    p.drawString(2.2*inch, 1.4*inch, "Color Id: " + c)
   

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
            name = i.custom_product_name
        else: 
            description = i.description
            name = i.product.name

        if description is None:
            description = ""
            name =""

        if i.mfgnum == None:
            i.mfgnum = ""

        if name == None:
            name = ""

        if count < 12:
            
            p.drawString(-.65*inch, x3*inch, i.number)
            p.drawString(-.2*inch, x3*inch, str(i.quantity))
            p.drawString(.3*inch, x3*inch, i.mfgnum)
            p.setFont("Helvetica", 12)
            p.drawString(1.55*inch, x3*inch, name + " - " + description) 
            p.setFont("Helvetica", 10)
            p.drawString(6.38*inch, x3*inch, "Needs Repair")
            p.setFont("Helvetica", 12)


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
   
            
        if count > 12:
            
            if count == 13 or count == 39 or count == 62:
                showpg = True
            
            if showpg == True:
                showpg = False
            
                p.showPage() 
                p.translate(1*inch, 1*inch) # Start a new page every time a multiple of 3 is reached
                p.line(-0.8*inch, -.8*inch,7.3*inch, -0.8*inch)# top
                x = -.4
                x1 = -0.8
                x3 = -.55

            if i.product.id  == 2:
                description = i.custom_product_description
                name = i.custom_product_name
            else: 
                description = i.description
                name = i.product.name

            if description is None:
                description = ""
                name =""


            
            
            p.drawString(-.65*inch, x3*inch, i.number)
            p.drawString(-.2*inch, x3*inch, str(i.quantity))
            p.drawString(.3*inch, x3*inch, i.mfgnum)
            p.drawString(1.55*inch, x3*inch, name + " -") 
            p.drawString(2.8*inch, x3*inch, description)
            p.setFont("Helvetica", 10)
            p.drawString(6.38*inch, x3*inch, "Needs Repair")
            p.setFont("Helvetica", 12)

            


            p.line(-0.8*inch, -.8*inch,7.3*inch, -0.8*inch)# top
            p.line(-0.8*inch, x*inch,7.3*inch, x*inch)# bottom
            
            p.line(-0.8*inch,x*inch,-0.8*inch,x1*inch)# 1
            p.line(-.4*inch,x*inch,-.4*inch,x1*inch)# 2 
            p.line(.2*inch,x*inch,.2*inch,x1*inch)# 3
            p.line(1.5*inch,x*inch,1.5*inch,x1*inch)# 4
            p.line(6.3*inch,x*inch,6.3*inch,x1*inch)# 5
            p.line(7.3*inch,x*inch,7.3*inch,x1*inch)# 6v
            p.line(-0.8*inch, x1*inch,7.3*inch, x1*inch)# top
            p.line(-0.8*inch, x*inch,7.3*inch, x*inch)# bottom
            x = x +.4
            x1 = x1 +.4
            x3 = x3+.4
            


        count +=1
    

    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    #response = HttpResponse(buffer, content_type='application/pdf')
    #response['Content-Disposition'] = 'inline; filename="invoice.pdf"'
    #buffer.seek(0)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=reportlab.pdf'
    response.write(buffer.read())
    buffer.close()

    return response



@login_required(login_url='invoice:loginPage')
def pdfTracker(request, workOrder_id):
    try:
        workOrder = WorkOrders.objects.get(pk=workOrder_id)
    except:
        workOrder = ""

    try:
        items = WorkOrderItem.objects.filter(workOrder=workOrder)
    except:
        items = ""

    try:
        primaryContact = ClientContact.objects.get(client=workOrder.client, status='Primary')
        primaryContact = f"{primaryContact.first_name} {primaryContact.last_name}"
    except:
        primaryContact = ""
    
    try:
        c = workOrder.color
        if c == None or c == "":
            c = "red"
    except:

        c = "red"
    
    
    logoPNG = 'static/img/simnarLogo.png'
    item_arr = []
    item_number_arr = []
    item_mfg_arr = []
    item_qty_arr = []
    item_type_arr = []
    item_issue_arr = []
    counter = 0

    try:
        user = User.objects.get(username=workOrder.created_by)
        recievingTech = f"{user.first_name[0]} {user.last_name[0]}"

    except:
        # Handle the case when the user with the given username doesn't exist
        recievingTech = ""
    
    for item in items:
        item_number_arr.append(item.number)
        item_qty_arr.append(item.quantity)
        item_type_arr.append(item.product.product_type.name)
        item_mfg_arr.append(item.mfgnum)
        if item.issue == "" or item.issue == None:
            item.issue = ""
        
        item_issue_arr.append(item.issue)
        
        if item.product.id == 2:
            item_arr.append(item.custom_product_name)
            print("Other")
            
        else:
            item_arr.append(item.product.name)





    buffer = io.BytesIO()

    # Create the PDF object with landscape orientation, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=landscape(letter), bottomup=0)

    ctc = .3
    logo = -.75
    account = -.7
    accountName = -.1

    address = -.38
    contact = -.1

    rt = .57
    dispo = 1.1

    date_r = 0.35
    date_rb = .05

    circle = 1.9
    circleNum = 1.78
    numID = 1.7
    num = 2.0
    colorId = 1.3

    color_ = 1.25
    instname = .45
    manufct = .18
    isnttype = .42
    quantity = 0.0
    
    l1x1 = -.15
    l1x2 = 2.3

    l2x1 = -.4
    l4x1 = .4
    l5x1 = .33
    l5x2 = 1.0
    l6x1 = 1.6
    l6x2 = 2.3

    l7x1 = .3
    l7x2 = 1.2
    l8x1 = 0.0
    l8x2 = .9

    l9x1 = -.7
    l9x2 = 2.35
    l10x1 = .18
    l10x2 = 1.2
    l11x1 = 1.63
    l11x2 = 2.3
    l12x2 = 2.3
    l13x1 = -.1
    l13x2 = .3


    x = -0.6
    x_ = -0.8
    x1 = 2.4
    x1_ = 2.6
    x3 = 1.4

    x5 = 1.0

    x2 = -.7

    p.translate(1*inch, 1*inch)  # Adjust as needed for your content placement

    for i in item_arr:


        p.line(x_*inch, -0.8*inch, x1_*inch, -0.8*inch)  # Top horizontal line total
        p.line(x_*inch, 7.2*inch, x_*inch, -0.8*inch)  # Right first vertical line
        p.line(x1_*inch, 7.2*inch, x1_*inch, -0.8*inch)  # Left vertical line
        p.line(x_*inch, 7.2*inch, x1_*inch, 7.2*inch)  # Bottom horizontal line total

        p.setFont("Helvetica", 10)
        p.saveState()
        p.scale(1,-1)
        p.drawImage(logoPNG, logo*inch, .1 * inch, width=70, height=30, mask=[0,0,0,0,0,0])
        p.restoreState()
        p.setFont("Helvetica-Bold", 10)
        p.drawString(ctc*inch, -.2*inch, "Customer Repair Tracking Card")
        
        p.setFont("Helvetica", 10)
        p.drawString(account*inch, .2*inch, "Account: ")
        p.line(l1x1*inch, .25*inch,l1x2*inch, .25*inch)
        p.drawString(accountName*inch, .2*inch, workOrder.client.name)
        
        p.drawString(account*inch, .5*inch, "City: ")
        p.line(l2x1*inch, .55*inch,l1x2*inch, .55*inch)
        p.drawString(address*inch, .5*inch, workOrder.client.address)
        
        
        p.drawString(account*inch, .8*inch, "Contact: ")
        p.line(l1x1*inch, .825*inch,l1x2*inch, .825*inch)
        p.drawString(contact*inch, .8*inch, primaryContact)

        p.drawString(account*inch, 1.1*inch, "Customer P.O. #:")
        p.line(l4x1*inch, 1.15*inch,l1x2*inch, 1.15*inch)

        p.drawString(account*inch, 1.4*inch, "Receiving Tech: ")
        p.line(l5x1*inch, 1.42*inch,l5x2*inch, 1.42*inch)
        p.drawString(rt*inch, 1.4*inch, recievingTech)

        p.drawString(dispo*inch, 1.4*inch, "Dispo #: ")
        p.line(l6x1*inch, 1.42*inch,l6x2*inch, 1.42*inch)

        p.drawString(account*inch, 1.7*inch, "Date Recieved:")
        p.line(l7x1*inch, 1.72*inch,l7x2*inch, 1.72*inch)
        p.drawString(date_r*inch, 1.7*inch, workOrder.created_at.strftime('%Y-%m-%d'))
        
        p.drawString(account*inch, 2.0*inch, "Return By:")
        p.line(l8x1*inch, 2.02*inch,l8x2*inch, 2.02*inch)
        p.drawString(date_rb*inch, 2.0*inch, workOrder.return_by.strftime('%Y-%m-%d'))

        p.setFont("Helvetica-Bold", 10.5)
        p.drawString(account*inch, 2.3*inch, "Inst. Description/Make/Model/Serial#/Color:")
        p.line(l9x1*inch, 2.32*inch,l9x2*inch, 2.32*inch)
        
        p.setFont("Helvetica", 10)
        p.drawString(account*inch, 2.6*inch, "Instrument Name: ")
        p.line(l4x1*inch, 2.62*inch,l1x2*inch, 2.62*inch)
        p.drawString(instname*inch, 2.6*inch, item_arr[counter])

        p.drawString(account*inch, 2.9*inch, "Manufacter #: ")
        p.line(l10x1*inch, 2.92*inch,l10x2*inch, 2.92*inch)
        p.drawString(manufct*inch, 2.9*inch, item_mfg_arr[counter])

        p.drawString(color_*inch, 2.9*inch, "Color: ")
        p.line(l11x1*inch, 2.92*inch,l11x2*inch, 2.92*inch)

        p.drawString(account*inch, 3.2*inch, "Instrument Type: ")
        p.line(l4x1*inch, 3.22*inch,l12x2*inch, 3.22*inch)
        p.drawString(isnttype*inch, 3.2*inch, item_type_arr[counter])

        p.drawString(account*inch, 3.5*inch, "Quantity: ")
        p.line(l13x1 *inch, 3.52*inch,l13x2*inch, 3.52*inch)
        p.drawString(quantity*inch, 3.5*inch, str(item_qty_arr[counter]))

        p.setFont("Helvetica-Bold", 10.5)
        p.drawString(account*inch, 3.8*inch, "Work Required/Requested/ Tech's Discovery:")
        p.line(l9x1*inch, 3.82*inch,l9x2*inch, 3.82*inch)
        p.setFont("Helvetica", 10)
        

        p.line(l9x1*inch, 4.13*inch,l9x2*inch, 4.13*inch)
        p.line(l9x1*inch, 4.43*inch,l9x2*inch, 4.43*inch)
        p.line(l9x1*inch, 4.73*inch,l9x2*inch, 4.73*inch)

        itemdesc = item_issue_arr[counter]
        part1 = itemdesc[0:45]
        part2 = itemdesc[50:100]
        part3 = itemdesc[90:135]


        
        p.drawString(account*inch, 4.1*inch, part1)
        p.drawString(account*inch, 4.4*inch, part2 )
        p.drawString(account*inch, 4.7*inch, part3)


        p.drawString(x2*inch, 7*inch, "Property of Simnar Surgical")
        p.setFillColor(c)
        p.circle(circle* inch, 6.2 * inch, 0.5 * inch, fill=1)

        fill_color = colors.black
        p.setFillColor(fill_color)
        p.setFont("Helvetica", 30)
        p.drawString(numID*inch, 5.45*inch, "#")
        p.drawString(num*inch, 5.45*inch, str(item_number_arr[counter]))
        p.setFont("Helvetica", 10)
        p.drawString(colorId*inch, 7*inch, "Color ID: "+ c)
        



        



        x = x + 3.6
        x_ = x_ + 3.6
        x1 = x1 + 3.6
        x1_ = x1_ + 3.6
        x2 = x2 + 3.6
        x3 = x3 + 3.6

        logo = logo + 3.6
        ctc = ctc + 3.6
        account = account + 3.6
        circle = circle + 3.6
        circleNum = circleNum + 3.6
        accountName = accountName + 3.6
        rt = rt + 3.6
        dispo = dispo + 3.6
        date_r = date_r + 3.6
        date_rb = date_rb + 3.6

        address = address + 3.6
        contact = contact + 3.6

        colorId = colorId + 3.6
        instname = instname + 3.6
        manufct = manufct + 3.6
        isnttype  = isnttype + 3.6
        quantity = quantity + 3.6
        numID = numID + 3.6
        num = num + 3.6

        color_ = color_ + 3.6
        l1x1 = l1x1 + 3.6
        l1x2 = l1x2 + 3.6
        l2x1= l2x1 + 3.6
        l4x1 = l4x1 + 3.6
        l5x1 = l5x1 + 3.6
        l5x2 = l5x2 + 3.6
        l6x1 = l6x1 + 3.6
        l6x2 = l6x2 + 3.6
        l7x1 = l7x1 + 3.6
        l7x2 = l7x2 + 3.6
        l8x1 = l8x1 + 3.6
        l8x2 = l8x2 + 3.6
        l9x1 = l9x1 + 3.6
        l9x2 = l9x2 + 3.6
        l10x1 = l10x1 + 3.6
        l10x2 = l10x2 + 3.6
        l11x1  = l11x1 + 3.6
        l11x2 = l11x2 + 3.6
        l12x2 = l12x2 + 3.6
        l13x1 = l13x1 + 3.6
        l13x2 = l13x2 + 3.6
        

        if (counter + 1) % 3 == 0 and (counter + 1) < len(item_arr):
            
            p.showPage() 
            p.translate(1*inch, 1*inch) # Start a new page every time a multiple of 3 is reached
            ctc = .3
            logo = -.7
            account = -.7
            accountName = -.1

            address = -.38
            contact = -.1

            rt = .57
            dispo = 1.1

            date_r = 0.35
            date_rb = .05

            circle = 1.9
            circleNum = 1.78
            numID = 1.7
            num = 2.0
            colorId = 1.3

            color_ = 1.25
            instname = .45
            manufct = .18
            isnttype = .42
            quantity = 0.0
            
            l1x1 = -.15
            l1x2 = 2.3

            l2x1 = -.4
            l4x1 = .4
            l5x1 = .33
            l5x2 = 1.0
            l6x1 = 1.6
            l6x2 = 2.3

            l7x1 = .3
            l7x2 = 1.2
            l8x1 = 0.0
            l8x2 = .9

            l9x1 = -.7
            l9x2 = 2.35
            l10x1 = .18
            l10x2 = 1.2
            l11x1 = 1.63
            l11x2 = 2.3
            l12x2 = 2.3
            l13x1 = -.1
            l13x2 = .3


            x = -0.6
            x_ = -0.8
            x1 = 2.4
            x1_ = 2.6
            x3 = 1.4


            x2 = -.7

        counter +=1
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="invoice.pdf"'

    return response

