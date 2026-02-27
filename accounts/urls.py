from django.urls import path
from .views import RegisterView, VerifyOTPView, ResendOTPView, MarkAsPaidView, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('mark-paid/', MarkAsPaidView.as_view(), name='mark_paid'),
    path('profile/', ProfileView.as_view(), name='profile'),
]