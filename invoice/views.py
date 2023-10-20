from django.shortcuts import render, redirect


def index(request):
    context= {}
    return render(request, 'index/index.html', context)



def createInvoice(request):

    context = {}

    return render(request, 'invoice/createInvoice.html', context)

def invoiceHistory(request):

    context = {}

    return render(request, 'invoice/invoiceHistory.html', context)

def addProductsClients(request):

    context = {}

    return render(request, 'invoice/addProductsClients.html', context)