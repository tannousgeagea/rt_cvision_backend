
from django.db import models
from instances.models import ServiceInstance

class UpstreamDefinition(models.Model):
    """
    Defines a global upstream endpoint that can be assigned to any service instance.
    """
    name = models.CharField(max_length=100, unique=True)
    route = models.CharField(max_length=255, help_text="The endpoint route, e.g., /api/status")
    method = models.CharField(
        max_length=10, 
        choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE')],
        default='GET'
    )
    description = models.TextField(blank=True, null=True, help_text="Description of what this upstream does")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'upstream_definition'
        verbose_name = "Upstream Definition"
        verbose_name_plural = "Upstream Definitions"
        ordering = ['route']

    def __str__(self):
        return f"{self.name} ({self.method} {self.route})"


class ServiceUpstream(models.Model):
    """
    Associates an upstream definition with a specific rtcvision service instance.
    Allows for customization of the route or method if required.
    """
    service_instance = models.ForeignKey(
        ServiceInstance,
        on_delete=models.CASCADE,
        related_name='upstreams'
    )
    upstream_definition = models.ForeignKey(
        UpstreamDefinition,
        on_delete=models.CASCADE,
        related_name='service_assignments'
    )
    # Optional override for the route or method if a service needs custom behavior
    custom_route = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Optional custom route for this service instance"
    )
    custom_method = models.CharField(
        max_length=10,
        choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE')],
        blank=True,
        null=True,
        help_text="Optional custom HTTP method"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'service_upstream'
        verbose_name = "Service Upstream"
        verbose_name_plural = "Service Upstreams"
        ordering = ['service_instance', 'upstream_definition']
        unique_together = ('service_instance', 'upstream_definition')

    def __str__(self):
        return f"{self.service_instance} -> {self.upstream_definition}"
