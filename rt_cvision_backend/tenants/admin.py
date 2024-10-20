from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline, StackedInline
from .models import Tenant, Plant, Domain, ServiceInstance, APIControl

# Inline for Plant in Tenant Admin
class PlantInline(TabularInline):
    model = Plant
    extra = 1  # Number of empty forms to display
    fields = ('plant_name', 'location', 'language', 'is_active')
    show_change_link = True

# Inline for Domain in Tenant Admin
class DomainInline(TabularInline):
    model = Domain
    extra = 1
    fields = ('domain_name',)
    show_change_link = True

# Inline for ServiceInstance in Plant Admin
class ServiceInstanceInline(TabularInline):
    model = ServiceInstance
    extra = 1
    fields = ('service_name', 'instance_name', 'api_base_url', 'status', 'is_active')
    show_change_link = True

# Inline for APIControl in ServiceInstance Admin
class APIControlInline(TabularInline):
    model = APIControl
    fields = ('api_token', 'rate_limit')
    can_delete = False  # Only one APIControl per ServiceInstance, disable deletion
    extra = 0
    show_change_link = True

@admin.register(Tenant)
class TenantAdmin(ModelAdmin):
    list_display = ('tenant_id', 'name', 'default_language', 'is_active', 'created_at')
    list_filter = ('is_active', 'default_language')
    search_fields = ('name', 'tenant_id')
    ordering = ('name',)
    inlines = [PlantInline, DomainInline]  # Include Plant and Domain inlines

@admin.register(Plant)
class PlantAdmin(ModelAdmin):
    list_display = ('tenant', 'plant_name', 'location', 'language', 'is_active', 'created_at')
    list_filter = ('is_active', 'language')
    search_fields = ('plant_name', 'location')
    ordering = ('plant_name',)
    inlines = [ServiceInstanceInline]  # Include ServiceInstance inline

@admin.register(Domain)
class DomainAdmin(ModelAdmin):
    list_display = ('tenant', 'domain_name', 'created_at')
    search_fields = ('domain_name',)
    ordering = ('domain_name',)

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
