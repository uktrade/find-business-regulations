# Generated by Django 4.2.19 on 2025-02-27 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataresponsemodel",
            name="source_date_issued",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="dataresponsemodel",
            name="source_date_modified",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="dataresponsemodel",
            name="source_date_valid",
            field=models.TextField(blank=True, null=True),
        ),
    ]
