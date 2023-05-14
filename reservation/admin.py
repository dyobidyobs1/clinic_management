from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea, CharField
from django import forms
from django.db import models

class UserAdminConfig(UserAdmin):
    model = CustomUser
    search_fields = ('username', 'email')
    list_filter = ('first_name', 'is_active', 'is_staff', 'is_doctor')
    list_display = ('username', 'id', 'email','is_active', 'is_staff', 'is_doctor')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_doctor')}),
    )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 60})}
    }
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                    'is_active',
                    'is_staff',
                    'is_doctor',
                ),
            },
        ),
    )


admin.site.register(CustomUser, UserAdminConfig)
admin.site.register(ReserveConsulation)
admin.site.register(Results)
admin.site.register(Services)
admin.site.register(Facilites)
admin.site.register(Speciality)
admin.site.register(DoctorDetails)
admin.site.register(UserDetails)
admin.site.register(Messages)

@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    readonly_fields = ["reference_number","transac_id"]


@admin.register(ReservationFacilities)
class ReservationFacilitiesAdmin(admin.ModelAdmin):
    readonly_fields = ["reference_number"]