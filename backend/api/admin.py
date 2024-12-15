from django.contrib import admin
from .views import *

# Register your models here.
admin.site.register(Customer)
admin.site.register(Account)
admin.site.register(Card)
admin.site.register(Transaction)
admin.site.register(SavedRecipient)
admin.site.register(Loan)
admin.site.register(ExchangeRate)
admin.site.register(Branch)
admin.site.register(Bankomat)