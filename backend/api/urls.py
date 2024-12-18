from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('update-info/', views.update_customer, name='update-info'),
    path('reset-password/', views.reset_password, name='reset-password'),
    path('open-account/', views.open_account, name='open-account'),
    path('get-savings-balance/', views.get_savings_account_balance, name='get-balance'),
    path('get-checking-balance/', views.get_checking_account_balance, name='get-balance'),
    path('transfer/', views.transfer, name='make-transaction'),
    path('deposit/', views.deposit, name='make-deposit'),
    path('withdraw/', views.withdraw, name='make-withdrawal'),
    path('transactions/', views.get_transactions, name='get-transactions'),
    path('close-account/', views.close_account, name='close-account'),
    path('get-branches/', views.get_branches, name='get-branches'),
]