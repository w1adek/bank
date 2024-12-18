import re

from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from . import models
from . import serializers
    
# Create your views here.
@api_view(['POST'])
def register(request):
    if models.Customer.objects.filter(phone=re.sub(r'\D', '', request.data['phone'])).exists():
        return Response({'phone': 'customer with this phone already exists.'},
                        status=status.HTTP_400_BAD_REQUEST)
        
    serializer = serializers.CustmerRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def open_account(request):
    customer_id = request.user.id
    print(customer_id)
    type = request.data['type']
    
    if models.Account.objects.filter(customer_id=customer_id, type=type).exists():
        return Response({'type': 'this account type already exists for customer.'},
                        status=status.HTTP_400_BAD_REQUEST)
    
    serializer = serializers.AccountOpenSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(customer_id=customer_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_customer(request):
    customer = models.Customer.objects.get(id=request.user.id)

    serializer = serializers.CustomerUpdateSerializer(customer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_password(request):
    customer = models.Customer.objects.get(id=request.user.id)

    serializer = serializers.UpdatePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.update_password(customer, serializer.validated_data)
        return Response({"message": "password updated successfully."}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_checking_account_balance(request):
    customer = request.user
    account = models.Account.objects.filter(customer=customer, type='checking').first()
    
    if not account:
        return Response({"error": "No checking account found."}, status=status.HTTP_404_NOT_FOUND)

    return Response({"balance": str(account.balance)}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_savings_account_balance(request):
    customer = request.user
    account = models.Account.objects.filter(customer=customer, type='savings').first()
    
    if not account:
        return Response({"error": "no savings account found."}, status=status.HTTP_404_NOT_FOUND)

    return Response({"balance": str(account.balance)}, status=status.HTTP_200_OK)


