from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('update-info/', views.update_customer, name='update-info'),
    path('update-password/', views.update_password, name='update-password'),
    path('open-account/', views.open_account, name='open-account'),
    path('get-savings-balance/', views.get_savings_account_balance, name='get-balance'),
    path('get-checking-balance/', views.get_checking_account_balance, name='get-balance'),
]