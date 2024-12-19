import re

from django.db.models import Sum, Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from decimal import Decimal
from random import randint
from django.utils import timezone
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
    print(account)
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
        status='completed'
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
        status='completed'
    )
    transaction.save()
    account.balance -= amount
    account.save()
    return Response({"message": "withdrawal successful."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer(request):
    try:
        from_account = models.Account.objects.get(customer_id=request.user.pk, pk=request.data['account_id'])
        to_account = models.Account.objects.get(pk=request.data['to_account_id'])
    except models.Account.DoesNotExist:
        return Response({"error": "account not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if from_account == to_account:
        return Response({"error": "cannot transfer to the same account."}, status=status.HTTP_400_BAD_REQUEST)
    
    amount = Decimal(request.data['amount'])
    if amount <= 0:
        return Response({"error": "amount must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
    if from_account.balance < amount:
        return Response({"error": "insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)

    if amount >= 1000:
        transaction = models.Transaction.objects.create(
            account=from_account,
            recipient=to_account,
            type='transfer',
            amount=request.data['amount'],
            status='pending'
        )
        transaction.save()
        from_account.balance -= amount
        from_account.save()
        return Response({"message": "transfer pending approval."}, status=status.HTTP_200_OK)
        
    transaction = models.Transaction.objects.create(
        account=from_account,
        recipient=to_account,
        type='transfer',
        amount=request.data['amount'],
        status='completed'
    )
    transaction.save()
    from_account.balance -= amount
    from_account.save()
    to_account.balance += amount
    to_account.save()
    return Response({"message": "transfer successful."}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_pending_transactions(request):
    transactions = models.Transaction.objects.filter(status='pending')
    serializer = serializers.TransactionSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)\
        

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def approve_transaction(request):
    try:
        transaction = models.Transaction.objects.get(pk=request.data.get('transaction_id'))
    except models.Transaction.DoesNotExist:
        return Response({"error": "transaction not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if transaction.status == 'completed':
        return Response({"error": "transaction already completed."}, status=status.HTTP_400_BAD_REQUEST)
    
    transaction.status = 'completed'
    transaction.save()
    transaction.recipient.balance += transaction.amount
    transaction.recipient.save()
    return Response({"message": "transaction approved."}, status=status.HTTP_200_OK)


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
        bankomats = models.Bankomat.objects.filter(address=branch)

        bankomat_list = [
            {
                "cash_deposit": bankomat.cash_deposit
            }
            for bankomat in bankomats
        ]

        data.append({
            "branch_address": branch.address,
            "open_time": branch.open_time,
            "close_time": branch.close_time,
            "bankomats": bankomat_list
        })

    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_exchange_rates(request):
    exchange_rates = models.ExchangeRate.objects.all()

    data = [
        {
            "currency": exchange_rate.currency,
            "multiplier": str(exchange_rate.multiplier)
        }
        for exchange_rate in exchange_rates
    ]

    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def issue_card(request):
    account_id = request.data.get('account_id')
    card_type = request.data.get('type')
    daily_limit = request.data.get('daily_limit')

    if not account_id or not card_type or not daily_limit:
        return Response(
            {"error": "account id, card type, and daily limit are required."},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        account = models.Account.objects.get(pk=account_id, customer_id=request.user.pk)
    except models.Account.DoesNotExist:
        return Response(
            {"error": "account not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    if daily_limit <= 0:
        return Response({"error": "daily limit must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
    
    valid_card_types = [card[0] for card in models.Card.CARD_TYPES]
    if card_type not in valid_card_types:
        return Response(
            {"error": "Invalid card type. It must be either 'debit' or 'credit'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    def generate_unique_card_number():
        while True:
            card_number = ''.join([str(randint(0, 9)) for _ in range(16)])
            if not models.Card.objects.filter(card_number=card_number).exists():
                return card_number

    card_number = generate_unique_card_number()
    expiry_date = timezone.now().date().replace(year=timezone.now().year + 3)

    card = models.Card.objects.create(
        account=account,
        card_number=card_number,
        type=card_type,
        expiry_date=expiry_date,
        daily_limit=Decimal(daily_limit)
    )

    return Response(
        {"message": "card issued successfully."},
        status=status.HTTP_200_OK
    )
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_card_details(request):
    card_id = request.data.get('card_id')

    if not request.data:
        return Response({"error": "card id is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        card = models.Card.objects.get(pk=card_id, account__customer=request.user)
    except models.Card.DoesNotExist:
        return Response({"error": "card not found."}, status=status.HTTP_404_NOT_FOUND)
    
    card_data = {
        "card_number": card.card_number,
        "type": card.type,
        "expiry_date": card.expiry_date,
        "daily_limit": str(card.daily_limit)
    }

    return Response(card_data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def set_daily_limit(request):
    card_id = request.data.get('card_id')
    daily_limit = request.data.get('daily_limit')

    if not card_id or not daily_limit:
        return Response({"error": "card id and new limit are required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        card = models.Card.objects.get(pk=card_id, account__customer=request.user)
    except models.Card.DoesNotExist:
        return Response({"error": "Card not found."}, status=status.HTTP_404_NOT_FOUND)

    daily_limit = Decimal(daily_limit)
    
    if daily_limit <= 0:
        return Response({"error": "daily limit must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
    
    card.daily_limit = daily_limit
    card.save()

    return Response({"message": f"daily limit updated to {daily_limit} for card {card.card_number}"},
                    status=status.HTTP_200_OK)
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_saved_recipient(request):
    customer = request.user
    account_id = request.data.get('account_id')
    recipient_account_id = request.data.get('recipient_account_id')

    if account_id == recipient_account_id:
        return Response(
            {"error": "account_id and recipient_account_id cannot be the same."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not account_id or not recipient_account_id:
        return Response(
            {"error": "account_id and recipient_account_id are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        account = models.Account.objects.get(pk=account_id, customer_id=customer)
    except models.Account.DoesNotExist:
        return Response(
            {"error": "account not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        recipient_account = models.Account.objects.get(pk=recipient_account_id)
    except models.Account.DoesNotExist:
        return Response(
            {"error": "recipient account not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    if models.SavedRecipient.objects.filter(account=account, recipient=recipient_account).exists():
        return Response(
            {"error": "recipient already saved."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    models.SavedRecipient.objects.create(account=account, recipient=recipient_account)

    return Response(
        {"message": "recipient added successfully."},
        status=status.HTTP_201_CREATED
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_saved_recipient(request):
    customer = request.user
    account_id = request.data.get('account_id')
    recipient_account_id = request.data.get('recipient_account_id')
    
    if account_id == recipient_account_id:
        return Response(
            {"error": "account_id and recipient_account_id cannot be the same."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not account_id or not recipient_account_id:
        return Response(
            {"error": "account_id and recipient_account_id are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        account = models.Account.objects.get(pk=account_id, customer_id=customer)
    except models.Account.DoesNotExist:
        return Response(
            {"error": "account not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        recipient_account = models.Account.objects.get(pk=recipient_account_id)
    except models.Account.DoesNotExist:
        return Response(
            {"error": "recipient account not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    saved_recipient = models.SavedRecipient.objects.filter(
        account=account, recipient=recipient_account)

    if not saved_recipient:
        return Response(
            {"error": "recipient not found in saved list."},
            status=status.HTTP_404_NOT_FOUND
        )

    saved_recipient.delete()

    return Response(
        {"message": "recipient removed successfully."},
        status=status.HTTP_200_OK
    )
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saved_recipients(request):
    customer = request.user
    account_id = request.data.get('account_id')

    if not account_id:
        return Response({"error": "account_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        account = models.Account.objects.get(pk=account_id, customer_id=customer)
    except models.Account.DoesNotExist:
        return Response({"error": "account not found."}, status=status.HTTP_404_NOT_FOUND)

    saved_recipients = models.SavedRecipient.objects.filter(account=account)
    data = [{"recipient_account_id": saved_recipient.recipient.id,}
        for saved_recipient in saved_recipients
    ]

    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_for_loan(request):
    serializer = serializers.LoanSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def approve_loan(request, loan_id):
    try:
        loan = models.Loan.objects.get(id=loan_id)
        if loan.approved:
            return Response({'error': 'loan already approved'}, status=status.HTTP_400_BAD_REQUEST)
        loan.approved = True
        loan.save()
        return Response({'status': 'loan approved'}, status=status.HTTP_200_OK)
    except models.Loan.DoesNotExist:
        return Response({'error': 'loan not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_loans(request):
    loans = models.Loan.objects.filter(account_id=request.user.id)
    if not loans.exists():
        return Response({'error': 'no loans found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = serializers.LoanSerializer(loans, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_loan_payment(request, loan_id):
    try:
        loan = models.Loan.objects.get(id=loan_id)
        if 'remaining_amount' in request.data:
            if Decimal(request.data['remaining_amount']) <= 0:
                return Response({'error': 'remaining amount must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
            loan.remaining_amount -= Decimal(request.data['remaining_amount'])
        serializer = serializers.LoanSerializer(loan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except models.Loan.DoesNotExist:
        return Response({'error': 'loan not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_loan_details(request, loan_id):
    try:
        loan = models.Loan.objects.get(id=loan_id, account_id=request.user.id)
        data = {
            "account_id": loan.account_id,
            "interest_rate": str(loan.interest_rate),
            "total_amount": str(loan.total_amount),
            "remaining_amount": str(loan.remaining_amount),
            "start_date": loan.start_date,
            "end_date": loan.end_date,
            "payment_schedule": loan.payment_schedule
        }
        return Response(data, status=status.HTTP_200_OK)
    except models.Loan.DoesNotExist:
        return Response({'error': 'loan not found'}, status=status.HTTP_404_NOT_FOUND)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_financial_report(request):
    account_id = request.query_params.get('account_id')
    report_type = request.query_params.get('report_type', 'summary')
    
    transactions = models.Transaction.objects.filter(
        Q(account__customer=request.user) | Q(recipient__customer=request.user),
        status='completed'
    )

    if account_id:
        transactions = transactions.filter(Q(account_id=account_id) | Q(recipient_id=account_id))

    total_deposits = transactions.filter(type='deposit').aggregate(total=Sum('amount'))['total'] or Decimal(0)
    total_withdrawals = transactions.filter(type='withdrawal').aggregate(total=Sum('amount'))['total'] or Decimal(0)
    total_transfers_out = transactions.filter(type='transfer', account__customer=request.user).aggregate(total=Sum('amount'))['total'] or Decimal(0)
    total_transfers_in = transactions.filter(type='transfer', recipient__customer=request.user).aggregate(total=Sum('amount'))['total'] or Decimal(0)

    if report_type == 'income':
        income = total_deposits + total_transfers_in
        return Response({"income": str(income)}, status=200)

    elif report_type == 'expenses':
        expenses = total_withdrawals + total_transfers_out
        return Response({"expenses": str(expenses)}, status=200)

    balance = total_deposits + total_transfers_in - (total_withdrawals + total_transfers_out)
    report = {
        "total_deposits": str(total_deposits),
        "total_withdrawals": str(total_withdrawals),
        "total_transfers_out": str(total_transfers_out),
        "total_transfers_in": str(total_transfers_in),
        "net_balance": str(balance)
    }

    return Response(report, status=status.HTTP_200_OK)