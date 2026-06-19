from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("Role Info", {
            "fields": ("role", "category", "reg_no", "phone")
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role Info", {
            "fields": ("role", "category", "reg_no", "phone")
        }),
    )


admin.site.register(User, CustomUserAdmin)
