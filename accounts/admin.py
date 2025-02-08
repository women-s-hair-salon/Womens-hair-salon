from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserType

# 1️⃣ Admin for UserType
@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Display ID and name in list view
    search_fields = ('name',)  # Enable search by name


# 2️⃣ Admin for CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Override the UserAdmin to use CustomUser model fields
    model = CustomUser
    list_display = ('id', 'full_name', 'phone_number', 'user_type', 'is_active', 'is_staff', 'date_joined', 'referral_code', 'referral_number')
    list_filter = ('user_type', 'is_active', 'is_staff')  # Filters for easy navigation
    search_fields = ('phone_number', 'first_name', 'last_name')  # Enable search by phone number, name
    ordering = ('-date_joined',)  # Display newest users first

    # Custom fieldsets for the user model
    fieldsets = (
        (None, {'fields': ('phone_number', 'first_name', 'last_name', 'password')}),
        ('Personal Info', {'fields': ('birthday', 'user_type', 'referral_code', 'referraler_code', 'referral_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Allow users to reset their passwords in admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'first_name', 'last_name', 'birthday', 'user_type')
        }),
    )

    # To manage the `password` field for `CustomUser`
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # When creating a new user
            obj.set_password(obj.password)  # Ensure password is hashed before saving
        super().save_model(request, obj, form, change)
