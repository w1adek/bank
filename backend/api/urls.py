from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.CustomerRegistrationView.as_view(), name='customer-registration'),
    #path('login/', views.CustomerLoginView.as_view(), name='customer-login'),
    path('open-account/', views.AccountOpenView.as_view(), name='account-opening'),
    path('branches/', views.BranchList.as_view(), name='branch-list'),
]