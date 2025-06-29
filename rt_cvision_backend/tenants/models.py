from django.db import models
import pytz
from metadata.models import (
    Language
)


REGION_TIMEZONE_MAP = {
    'US-East': 'America/New_York',
    'US-West': 'America/Los_Angeles',
    'EU-West': 'Europe/London',
    'EU-Central': 'Europe/Berlin',
    'Asia-Pacific': 'Asia/Singapore',
    'Middle-East': 'Asia/Dubai',
}
REGION_CHOICES = [(key, key) for key in REGION_TIMEZONE_MAP.keys()]
PLAN_CHOICES = [
    ("starter", "Starter"),
    ("professional", "Professional"),
    ("enterprise", "Enterprise"),
]

# Create your models here.
class Tenant(models.Model):
    tenant_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, null=True, blank=True)
    default_language = models.ForeignKey(Language, models.RESTRICT)
    is_active = models.BooleanField(default=True, help_text="Indicates if the filter is currently active.")
    created_at = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)

    logo_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    region = models.CharField(
        max_length=100,
        choices=REGION_CHOICES,
        null=True,
        blank=True,
        help_text="Region tag for UI filtering (e.g., US-East)"
    )
    plan = models.CharField(
        max_length=50,
        choices=PLAN_CHOICES,
        default="starter",
        help_text="Subscription plan tier"
    )
    last_activity = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in pytz.all_timezones],
        default="Europe/Berlin",
        help_text="Timezone for the tenant"
    )

    class Meta:
        db_table = 'tenant'
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_tenant_name_constraint')
        ]
        
    def __str__(self):
        return f"{self.name}"
    
class Plant(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='plants')
    plant_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    language = models.ForeignKey(Language, models.RESTRICT)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)

    logo_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    region = models.CharField(
        max_length=100,
        choices=REGION_CHOICES,
        null=True,
        blank=True,
        help_text="Region tag for UI filtering (e.g., US-East)"
    )
    plan = models.CharField(
        max_length=50,
        choices=PLAN_CHOICES,
        default="starter",
        help_text="Subscription plan tier"
    )
    last_activity = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in pytz.all_timezones],
        default="Europe/Berlin",
        help_text="Timezone for the tenant"
    )

    class Meta:
        db_table = "plant"
        verbose_name = "Plant"
        verbose_name_plural = "Plants"
        ordering = ['plant_name']
        unique_together = ('tenant', 'plant_name')
        
    def __str__(self):
        return f'{self.plant_name} - {self.location}'
    
class Domain(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='domains')
    domain_name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'domain'
        verbose_name = "Domain"
        verbose_name_plural = "Domains"
        ordering = ['domain_name']
        constraints = [
            models.UniqueConstraint(fields=['domain_name'], name='unique_domain_constraint')
        ]

    def __str__(self):
        return self.domain_name
    