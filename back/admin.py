from django.contrib import admin
from django.core.cache import cache
from back.models import CustomerProfile, WorkerProfile, RepairRequest
from back.models.pricing_models import DeviceBasePrice, RepairKeyword


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


def _clear_pricing_cache(modeladmin, request, queryset):
    """Сбросить кеш цен после изменений."""
    cache.delete('pricing:base_prices')
    for device_type in queryset.values_list('device_type', flat=True).distinct():
        cache.delete(f'pricing:keywords:{device_type}')
_clear_pricing_cache.short_description = 'Сбросить кеш цен'


@admin.register(DeviceBasePrice)
class DevicePriceAdmin(admin.ModelAdmin):
    list_display = ('get_device_type_display', 'base_price_formatted')
    ordering = ('device_type',)
    actions = [_clear_pricing_cache]

    @admin.display(description='Тип устройства')
    def get_device_type_display(self, obj):
        return obj.get_device_type_display()

    @admin.display(description='Базовая цена')
    def base_price_formatted(self, obj):
        return f'{obj.base_price:,} ₸'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete('pricing:base_prices')


@admin.register(RepairKeyword)
class RepairKeywordAdmin(admin.ModelAdmin):
    list_display = ('phrase', 'get_device_type_display', 'price_multiplier',
                    'confidence_boost', 'repair_type', 'is_active')
    list_filter = ('device_type', 'repair_type', 'is_active')
    search_fields = ('phrase',)
    list_editable = ('price_multiplier', 'confidence_boost', 'is_active')
    ordering = ('device_type', 'repair_type', '-price_multiplier')
    actions = [_clear_pricing_cache]

    @admin.display(description='Устройство')
    def get_device_type_display(self, obj):
        return obj.get_device_type_display()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete(f'pricing:keywords:{obj.device_type}')

