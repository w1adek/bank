from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=255)
    secret_answer = models.CharField(max_length=50)
    password_hash = models.CharField(max_length=255)
    
    def __str__(self):
        return f'{self.name} {self.surname}'


class Account(models.Model):
    ACCOUNT_TYPES = (
        ('checking', 'Checking'),
        ('savings', 'Savings'),
        ('admin', 'Admin'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        unique_together = ('customer', 'type')
        
    def __str__(self):
        return f'{self.customer.name} {self.customer.surname} - {self.type}'


class Card(models.Model):
    CARD_TYPES = (
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, unique=True)
    type = models.CharField(max_length=20, choices=CARD_TYPES)
    expiry_date = models.DateField()
    daily_limit = models.DecimalField(max_digits=10, decimal_places=2)
    

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    )
    account = models.ForeignKey(Account, on_delete=models.DO_NOTHING, related_name='from_account')
    recipient = models.ForeignKey(Account, on_delete=models.DO_NOTHING, related_name='to_recipient')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=20)


class Loan(models.Model):
    account = models.ForeignKey(Account, on_delete=models.DO_NOTHING)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    payment_schedule = models.IntegerField()
    
    
class SavedRecipient(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account')
    recipient = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='saved_recipient')


class ExchangeRate(models.Model):
    currency = models.CharField(max_length=3, primary_key=True)
    multiplier = models.DecimalField(max_digits=10, decimal_places=4)


class Branch(models.Model):
    address = models.CharField(max_length=255, primary_key=True)
    open_time = models.TimeField()
    close_time = models.TimeField()


class Bankomat(models.Model):
    address = models.ForeignKey(Branch, on_delete=models.CASCADE)
    cash_deposit = models.BooleanField()