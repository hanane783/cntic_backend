from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):

    USER_TYPES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )

    type = models.CharField(max_length=20, choices=USER_TYPES)
    amount_to_pay = models.PositiveIntegerField(default=0)
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # تحديد المبلغ تلقائياً حسب نوع المستخدم
        if self.type == 'teacher':
            self.amount_to_pay = 250
        elif self.type == 'student':
            self.amount_to_pay = 200

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.type})"