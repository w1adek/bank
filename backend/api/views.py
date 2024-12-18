import re

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
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
def reset_password(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')
    secret_answer = request.data.get('secret_answer')

    if not email or not new_password or not secret_answer:
        return Response(
            {"error": "email, new password, and secret answer are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        customer = models.Customer.objects.get(email=email)
    except models.Customer.DoesNotExist:
        return Response(
            {"error": "customer with this email does not exist."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if customer.secret_answer.lower() != secret_answer.lower():
        return Response(
            {"error": "secret answer is incorrect."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    customer.password = serializers.make_password(new_password)
    customer.save()

    return Response(
        {"message": "password reset successfully."},
        status=status.HTTP_200_OK,
    )


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


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def deposit(request):
    try:
        account = models.Account.objects.get(customer_id=request.user.pk, id=request.data['account_id'])
    except models.Account.DoesNotExist:
        return Response({"error": "account not found."}, status=status.HTTP_404_NOT_FOUND)
    
    amount = Decimal(request.data['amount'])
    if amount <= 0:
        return Response({"error": "amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)

    transaction = models.Transaction.objects.create(
        account=account,
        recipient=account,
        type='deposit',
        amount=request.data['amount'],
        status='ok'
    )
    transaction.save()
    account.balance += amount
    account.save()
    return Response({"message": "deposit successful."}, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def withdraw(request):
    try:
        account = models.Account.objects.get(customer_id=request.user.pk, pk=request.data['account_id'])
    except models.Account.DoesNotExist:
        return Response({"error": "account not found."}, status=status.HTTP_404_NOT_FOUND)
    
    amount = Decimal(request.data['amount'])
    if amount <= 0:
        return Response({"error": "amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
    if account.balance < amount:
        return Response({"error": "insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)

    transaction = models.Transaction.objects.create(
        account=account,
        recipient=account,
        type='withdrawal',
        amount=request.data['amount'],
        status='ok'
    )
    transaction.save()
    account.balance -= amount
    account.save()
    return Response({"message": "withdrawal successful."}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transfer(request):
    try:
        from_account = models.Account.objects.get(customer_id=request.user.pk, pk=request.data['account_id'])
        to_account = models.Account.objects.get(pk=request.data['to_account_id'])
    except models.Account.DoesNotExist:
        return Response({"error": "account not found."}, status=status.HTTP_404_NOT_FOUND)
    
    amount = Decimal(request.data['amount'])
    if amount <= 0:
        return Response({"error": "amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
    if from_account.balance < amount:
        return Response({"error": "insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)

    transaction = models.Transaction.objects.create(
        account=from_account,
        recipient=to_account,
        type='transfer',
        amount=request.data['amount'],
        status='ok'
    )
    transaction.save()
    from_account.balance -= amount
    to_account.balance += amount
    from_account.save()
    to_account.save()
    return Response({"message": "transfer successful."}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transactions(request):
    customer = request.user
    print(customer)
    transactions = models.Transaction.objects.filter(account__customer=customer).order_by('-date', '-time')
    serializer = serializers.TransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def close_account(request):
    try:
        account = models.Account.objects.get(pk=request.data['account_id'], customer_id=request.user.pk)
    except models.Account.DoesNotExist:
        return Response({"error": "account not found."}, status=status.HTTP_404_NOT_FOUND)

    if account.balance != Decimal('0.00'):
        return Response(
            {"error": "account cannot be closed, balance must be zero."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    account.delete()
    return Response({"message": "account successfully closed."}, status=status.HTTP_200_OK,)


@api_view(['GET'])
def get_branches(request):
    branches = models.Branch.objects.all()

    data = []
    for branch in branches:
        # Corrected line: Access related Bankomat objects using the related_name or directly
        bankomats = models.Bankomat.objects.filter(address=branch)  # Changed from branches.Bankomat

        bankomat_list = [
            {
                "cash_deposit": bankomat.cash_deposit
            }
            for bankomat in bankomats  # Correctly iterate over bankomats
        ]

        data.append({
            "branch_address": branch.address,
            "open_time": branch.open_time,
            "close_time": branch.close_time,
            "bankomats": bankomat_list
        })

    return Response(data, status=status.HTTP_200_OK)