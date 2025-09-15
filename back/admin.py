from django.contrib import admin

# Register your models here.
# back/admin.py
from django.contrib import admin
from .models import CustomerProfile, WorkerProfile, RepairRequest

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username', 'phone_number')

@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'experience', 'rating', 'is_verified')
    list_filter = ('is_verified', 'specialization')
    search_fields = ('user__username', 'specialization')

@admin.register(RepairRequest)
class RepairRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'device_type', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'device_type', 'created_at')
    search_fields = ('title', 'description', 'address')
