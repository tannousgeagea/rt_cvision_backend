# Generated by Django 4.2 on 2024-10-26 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instances', '0002_endpoint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apicontrol',
            name='api_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
