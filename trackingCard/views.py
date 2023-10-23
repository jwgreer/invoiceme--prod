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




@login_required(login_url='invoice:loginPage')
def trackingCards(request):

    context = {}

    return render(request, 'tracking/addTracking.html', context)



@login_required(login_url='invoice:loginPage')
def pdfTracker(request):
    invoice_id = 62
    invoice = Invoice.objects.get(pk=invoice_id)
    items = InvoiceItem.objects.filter(invoice=invoice)
    item_arr = []
    counter = 0

    for item in items:
        quantity = 1
        i = 0
        if item.quantity > 1:
            quantity = item.quantity

        while i < quantity:
            product = item.product
            item_arr.append(item.product.name)

            i +=1



    buffer = io.BytesIO()

    # Create the PDF object with landscape orientation, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=landscape(letter), bottomup=0)

    x = -0.6
    x1 = 2.4
    x3 = 1.4

    x2 = -.5

    p.translate(1*inch, 1*inch)  # Adjust as needed for your content placement

    for i in item_arr:
        # Your content and drawing instructions go here

        p.line(x*inch, -0.5*inch, x1*inch, -0.5*inch)  # Top horizontal line total
        p.line(x*inch, 7.0*inch, x*inch, -0.5*inch)  # Right first vertical line
        p.line(x1*inch, 7.0*inch, x1*inch, -0.5*inch)  # Left vertical line
        p.line(x*inch, 7.0*inch, x1*inch, 7.0*inch)  # Bottom horizontal line total

        p.drawString(x2*inch, .0*inch, "Instrument Tracking Card")
        p.drawString(x2*inch, .5*inch, "Client Name: " + invoice.client.name)
        p.drawString(x2*inch, 1.0*inch, "Address: "+invoice.client.address)
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
        



        



        x = x + 3.6
        x1 = x1 + 3.6
        x2 = x2 + 3.6
        x3 = x3 + 3.6

        if (counter + 1) % 3 == 0 and (counter + 1) < len(item_arr):
            
            p.showPage() 
            p.translate(1*inch, 1*inch) # Start a new page every time a multiple of 3 is reached

            x = -0.6
            x1 = 2.4
            x2 = -.5
            x3 = 1.4

        counter +=1
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="invoice.pdf"'

    return response

