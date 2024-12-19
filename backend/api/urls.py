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
    path('get-exchange-rates/', views.get_exchange_rates, name='get-exchange-rates'),
    path('issue-card/', views.issue_card, name='issue-card'),
    path('get-card-details/', views.get_card_details, name='get-card-details'),
    path('set-daily-limit/', views.set_daily_limit, name='set-daily-limit'),
    path('add-saved-recipient/', views.add_saved_recipient, name='add-saved-recipient'),
    path('delete-saved-recipient/', views.delete_saved_recipient, name='delete-saved-recipient'),
    path('get-saved-recipients/', views.get_saved_recipients, name='get-saved-recipients'),
    path('get-pending-transactions/', views.get_pending_transactions, name='get-pending-transactions'),
    path('approve-transaction/', views.approve_transaction, name='approve-transaction'),
    path('generate-financial-report/', views.generate_financial_report, name='generate-financial-report'),
]