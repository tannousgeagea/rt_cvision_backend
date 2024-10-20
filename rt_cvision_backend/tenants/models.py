from django.db import models
from metadata.models import (
    Language
)

# Create your models here.
class Tenant(models.Model):
    tenant_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    default_language = models.ForeignKey(Language, models.RESTRICT)
    is_active = models.BooleanField(default=True, help_text="Indicates if the filter is currently active.")
    created_at = models.DateTimeField(auto_now_add=True)
    
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
    
class ServiceInstance(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=255)
    instance_name = models.CharField(max_length=255)
    api_base_url = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[('running', 'Running'), ('stopped', 'Stopped')], default='stopped')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'service_instance'
        verbose_name = "Service Instance"
        verbose_name_plural = "Service Instances"
        ordering = ['instance_name']
        unique_together = ('plant', 'instance_name')

    def __str__(self):
        return f'{self.service_name} - {self.instance_name}'

class APIControl(models.Model):
    service_instance = models.OneToOneField(ServiceInstance, on_delete=models.CASCADE, related_name='api_control')
    api_token = models.CharField(max_length=255)
    rate_limit = models.IntegerField(default=1000)  # Example field for API rate limiting
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_control'
        verbose_name = "API Control"
        verbose_name_plural = "API Controls"
        ordering = ['service_instance']  # Orders by the service instance name

    def __str__(self):
        return f'API Control for {self.service_instance.instance_name}'
    