from django.contrib import admin
from .views import *

# Register your models here.
admin.site.register(Customer)
admin.site.register(Account)
admin.site.register(Card)