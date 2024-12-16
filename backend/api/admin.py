from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Customer)
admin.site.register(models.Account)
admin.site.register(models.Card)
admin.site.register(models.Transaction)
admin.site.register(models.SavedRecipient)
admin.site.register(models.Loan)
admin.site.register(models.ExchangeRate)
admin.site.register(models.Branch)
admin.site.register(models.Bankomat)