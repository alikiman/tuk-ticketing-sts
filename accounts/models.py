from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_STUDENT = "student"
    ROLE_STAFF = "staff"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = (
        (ROLE_STUDENT, "Student"),
        (ROLE_STAFF, "Staff"),
        (ROLE_ADMIN, "Admin"),
    )

    CATEGORY_CHOICES = (
        ("fees", "Fees"),
        ("clearance", "Clearance"),
        ("results", "Results"),
        ("other", "Other"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True
    )

    reg_no = models.CharField(
    max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    phone = models.CharField(max_length=20, blank=True, null=True)

    profile_pic = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.username} - {self.role}"