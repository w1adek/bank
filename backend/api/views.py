from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from .models import *
from .serializers import *


# Create your views here.
def login(request):
    return HttpResponse("Login view")

def register(request):
    return HttpResponse("Register view")

class CustomerView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer