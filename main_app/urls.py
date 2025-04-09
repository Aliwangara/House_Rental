from django.urls import path
from . import views
from allauth.account import views as allauth_views

urlpatterns = [
    path('', views.home, name='home'),
    

  path('dashboard/', views.dashboard_router, name='dashboard'),
  path('dashboard/landlord/', views.landlord_dashboard, name='landlord_dashboard'),
  path('maintenance/all/', views.all_maintenance_requests, name='all_maintenance_requests'),
  path('dashboard/tenant/', views.tenant_dashboard, name='tenant_dashboard'),



 
  path('properties/', views.property_list, name='property_list'),
  path('all_properties/', views.all_properties, name='all_properties'),
  path('property/<int:pk>/', views.property_detail, name='property_detail'),
  path('properties/add/', views.add_property, name='add_property'),
  path('properties/edit/<int:pk>/', views.edit_property, name='edit_property'),
  path('properties/delete/<int:pk>/', views.delete_property, name='delete_property'),



  path('maintenance/submit/', views.submit_maintenance_request, name='submit_maintenance'),
  path('maintenance/my-requests/', views.tenant_requests, name='tenant_requests'),
  path('maintenance/all/', views.all_maintenance_requests, name='landlord_requests'),

      path('reports/', views.reports, name='reports'),


  path('payments/submit/', views.submit_payment, name='submit_payment'),
  path('payments/my/', views.tenant_payments, name='tenant_payments'),
  path('payments/all/', views.all_payments, name='landlord_payments'),
  path('payments/verify/<int:pk>/', views.verify_payment, name='verify_payment'),



  path('payments/receipt/<int:pk>/', views.generate_pdf_receipt, name='payment_receipt'),


 # Login and signup

    path('accounts/login/', allauth_views.LoginView.as_view(template_name='authentication/login.html'), name='account_login'),
    path('accounts/signup/', allauth_views.SignupView.as_view(template_name='authentication/signup.html'), name='account_signup'),
    path('accounts/logout/', allauth_views.LogoutView.as_view(), name='account_logout'),



]