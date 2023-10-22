from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required



@login_required(login_url='invoice:loginPage')
def trackingCards(request):

    context = {}

    return render(request, 'tracking/tracking.html', context)

# Create your views here.
