from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline, StackedInline
from .models import UpstreamDefinition, ServiceUpstream

@admin.register(UpstreamDefinition)
class UpstreamDefinitionAdmin(ModelAdmin):
    list_display = ('name', 'route', 'method', 'is_active')
    search_fields = ('name', 'route')

@admin.register(ServiceUpstream)
class ServiceUpstreamAdmin(ModelAdmin):
    list_display = ('service_instance', 'upstream_definition', 'is_active', 'created_at')
    list_filter = ('is_active',)