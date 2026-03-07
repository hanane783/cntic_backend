
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.mail import send_mail
from django.conf import settings


from .models import Account
from decorators import verified_required, paid_required, verified_and_paid_required
import random


class RegisterView(APIView):

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        user_type = request.data.get('type')

        if not username or not email or not password or not user_type:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if Account.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        if Account.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        if user_type not in ['student', 'others']:
            return Response({"error": "Invalid user type"}, status=status.HTTP_400_BAD_REQUEST)

        otp = random.randint(100000, 999999)

        user = Account(
            username=username,
            email=email,
            type=user_type,
            otp_code=otp,
            is_verified=False,
            is_paid=False
        )
        user.set_password(password)
        user.save()

        send_mail(
            subject="Your CNTIC Verification Code",
            message=f"Hello {username},\n\nYour OTP verification code is: {otp}\n\nThis code is required to activate your account.\n\nCNTIC Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {
                "message": "User registered successfully. Please check your email for the OTP code.",
                "amount_to_pay": user.amount_to_pay
            },
            status=status.HTTP_201_CREATED
        )


class VerifyOTPView(APIView):

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_verified:
            return Response({"message": "Account already verified"}, status=status.HTTP_200_OK)

        try:
            otp_int = int(otp)
        except (ValueError, TypeError):
            return Response({"error": "Invalid OTP format"}, status=status.HTTP_400_BAD_REQUEST)

        if user.otp_code != otp_int:
            return Response({"error": "Invalid OTP code"}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.otp_code = None
        user.save()

        return Response({"message": "Account verified successfully"}, status=status.HTTP_200_OK)


class ResendOTPView(APIView):

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_verified:
            return Response({"error": "Account already verified"}, status=status.HTTP_400_BAD_REQUEST)

        otp = random.randint(100000, 999999)
        user.otp_code = otp
        user.save()

        send_mail(
            subject="Your CNTIC Verification Code",
            message=f"Hello {user.username},\n\nYour new OTP verification code is: {otp}\n\nCNTIC Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "OTP resent successfully"}, status=status.HTTP_200_OK)


class MarkAsPaidView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        user_id = request.data.get('user_id')
        is_paid = request.data.get('is_paid')

        if user_id is None or is_paid is None:
            return Response({"error": "user_id and is_paid are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Account.objects.get(id=user_id)
        except Account.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user.is_paid = bool(is_paid)
        user.save()

        return Response(
            {
                "message": f"User payment status updated to {user.is_paid}",
                "user_id": user.id,
                "username": user.username,
                "is_paid": user.is_paid
            },
            status=status.HTTP_200_OK
        )


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _user_data(self, user):
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "type": user.type,
            "is_verified": user.is_verified,
            "is_paid": user.is_paid,
            "amount_to_pay": user.amount_to_pay
        }

    def get(self, request):
        return Response(self._user_data(request.user), status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        data = request.data

        if data.get("username"):
            user.username = data["username"]

        if data.get("email"):
            user.email = data["email"]

        user.save()

        return Response(self._user_data(user), status=status.HTTP_200_OK)