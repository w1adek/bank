from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Custom Manager for the Customer model
class CustomerManager(BaseUserManager):
    def get_by_natural_key(self, email):
        return self.get(email=email)
    

class Customer(AbstractBaseUser):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=255)
    secret_answer = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    objects = CustomerManager()

    def __str__(self):
        return f'{self.phone}, {self.email}, {self.address}'


class Account(models.Model):
    ACCOUNT_TYPES = (
        ('checking', 'Checking'),
        ('savings', 'Savings'),
    )
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
        
    def __str__(self):
        return f'{self.pk}, {self.type}, {self.balance}, {self.customer}'


class Card(models.Model):
    CARD_TYPES = (
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    type = models.CharField(max_length=20, choices=CARD_TYPES)
    expiry_date = models.DateField()
    daily_limit = models.DecimalField(max_digits=10, decimal_places=2)
    

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    )
    STATUSES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='from_account')
    recipient = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='to_recipient')
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    
    def __str__(self):
        return f'{self.pk}, {self.account}, {self.recipient}, {self.type}, {self.amount}, {self.date}, {self.time}, {self.status}'


class Loan(models.Model):
    PAYMENT_SHAEULES = (
        (6, '6 months'),
        (12, '12 months'),
        (24, '24 months'),
        (36, '36 months'),
        (48, '48 months'),
        (60, '60 months'),
    )
    INTEREST_RATES = (
        (0.05, '5%'),
        (0.1, '10%'),
        (0.15, '15%'),
        (0.2, '20%'),
        (0.25, '25%'),
    )
    account = models.ForeignKey(Account, on_delete=models.DO_NOTHING)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    payment_schedule = models.IntegerField()
    
    def __str__(self):
            return f'{self.pk}, {self.account}, {self.interest_rate}, {self.total_amount}, {self.remaining_amount}, {self.start_date}, {self.end_date}, {self.payment_schedule}'

   
    
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