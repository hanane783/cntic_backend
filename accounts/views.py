

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Account
import random


class RegisterView(APIView):

    def post(self, request):

        # 1️⃣ استلام البيانات
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        user_type = request.data.get('type')

        # 2️⃣ التحقق من الحقول المطلوبة
        if not username or not email or not password or not user_type:
            return Response(
                {"error": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3️⃣ منع تكرار username
        if Account.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4️⃣ منع تكرار الإيميل
        if Account.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 5️⃣ التحقق من نوع المستخدم
        if user_type not in ['student', 'teacher']:
            return Response(
                {"error": "Invalid user type"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 6️⃣ توليد OTP
        otp = random.randint(100000, 999999)

        # 7️⃣ إنشاء المستخدم (السعر يتحدد تلقائياً في save())
        user = Account(
            username=username,
            email=email,
            type=user_type,
            otp_code=otp,
            is_verified=False,
            is_paid=False
        )

        # 8️⃣ تشفير كلمة السر
        user.set_password(password)

        # 9️⃣ حفظ المستخدم
        user.save()

        # 🔟 الرد (نرجّع OTP فقط للتجربة)
        return Response(
            {
                "message": "User registered successfully",
                "otp": otp,  # فقط أثناء التطوير
                "amount_to_pay": user.amount_to_pay
            },
            status=status.HTTP_201_CREATED
        )