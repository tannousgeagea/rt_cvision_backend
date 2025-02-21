from django.db import models
from tenants.models import Plant

# Create your models here.
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
        return f'{self.plant.plant_name}: {self.instance_name}'

class APIControl(models.Model):
    service_instance = models.OneToOneField(ServiceInstance, on_delete=models.CASCADE, related_name='api_control')
    api_token = models.CharField(max_length=255, null=True, blank=True)
    rate_limit = models.IntegerField(default=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_control'
        verbose_name = "API Control"
        verbose_name_plural = "API Controls"
        ordering = ['service_instance']

    def __str__(self):
        return f'API Control for {self.service_instance.instance_name}'

class Endpoint(models.Model):
    # api_control = models.ForeignKey(APIControl, on_delete=models.CASCADE, related_name='endpoints')
    name = models.CharField(max_length=100, unique=True)
    route = models.CharField(max_length=255)
    method = models.CharField(max_length=10, choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE')], default='GET')
    description = models.TextField(blank=True, null=True, help_text="Description of what this endpoint does")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'endpoint'
        verbose_name = "Endpoint"
        verbose_name_plural = "Endpoints"
        ordering = ['route']
        unique_together = ('name', 'route') 

    def __str__(self):
        return f'{self.method} {self.route}'