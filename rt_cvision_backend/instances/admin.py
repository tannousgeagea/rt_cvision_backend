from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline, StackedInline
from .models import ServiceInstance, APIControl, Endpoint

class APIControlInline(TabularInline):
    model = APIControl
    fields = ('api_token', 'rate_limit')
    can_delete = False  # Only one APIControl per ServiceInstance, disable deletion
    extra = 0
    show_change_link = True

class EndpointInline(TabularInline):
    model = Endpoint
    extra = 1  # Displays one empty form for adding a new endpoint
    fields = ('route', 'method', 'description', 'is_active')
    show_change_link = True  # Enables link to view/edit Endpoint details

# Register your models here.
@admin.register(ServiceInstance)
class ServiceInstanceAdmin(ModelAdmin):
    list_display = ('plant', 'service_name', 'instance_name', 'api_base_url', 'status', 'is_active', 'created_at')
    list_filter = ('status', 'is_active')
    search_fields = ('service_name', 'instance_name')
    ordering = ('instance_name',)
    inlines = [APIControlInline]

@admin.register(APIControl)
class APIControlAdmin(ModelAdmin):
    list_display = ('service_instance', 'api_token', 'rate_limit', 'created_at')
    search_fields = ('api_token', 'service_instance__instance_name')
    ordering = ('service_instance',)
    
@admin.register(Endpoint)
class EndpointAdmin(ModelAdmin):
    list_display = ('name', 'route', 'method', 'is_active')
    list_filter = ('method', 'is_active')
    search_fields = ('route',)
    ordering = ('route',)