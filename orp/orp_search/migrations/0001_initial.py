# Generated by Django 4.2.16 on 2024-11-20 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DataResponseModel",
            fields=[
                ("title", models.TextField(blank=True, null=True)),
                ("identifier", models.TextField(blank=True, null=True)),
                ("publisher", models.TextField(blank=True, null=True)),
                ("publisher_id", models.TextField(blank=True, null=True)),
                ("language", models.TextField(blank=True, null=True)),
                ("format", models.TextField(blank=True, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("date_issued", models.DateField(blank=True, null=True)),
                ("date_modified", models.DateField(blank=True, null=True)),
                ("date_valid", models.TextField(blank=True, null=True)),
                ("sort_date", models.DateField(blank=True, null=True)),
                ("audience", models.TextField(blank=True, null=True)),
                ("coverage", models.TextField(blank=True, null=True)),
                ("subject", models.TextField(blank=True, null=True)),
                ("type", models.TextField(blank=True, null=True)),
                ("license", models.TextField(blank=True, null=True)),
                ("regulatory_topics", models.TextField(blank=True, null=True)),
                ("status", models.TextField(blank=True, null=True)),
                (
                    "date_uploaded_to_orp",
                    models.DateField(blank=True, null=True),
                ),
                ("has_format", models.TextField(blank=True, null=True)),
                ("is_format_of", models.TextField(blank=True, null=True)),
                ("has_version", models.TextField(blank=True, null=True)),
                ("is_version_of", models.TextField(blank=True, null=True)),
                ("references", models.TextField(blank=True, null=True)),
                ("is_referenced_by", models.TextField(blank=True, null=True)),
                ("has_part", models.TextField(blank=True, null=True)),
                ("is_part_of", models.TextField(blank=True, null=True)),
                ("is_replaced_by", models.TextField(blank=True, null=True)),
                ("replaces", models.TextField(blank=True, null=True)),
                (
                    "related_legislation",
                    models.TextField(blank=True, null=True),
                ),
                ("id", models.TextField(primary_key=True, serialize=False)),
                (
                    "score",
                    models.IntegerField(blank=True, default=0, null=True),
                ),
            ],
        ),
    ]
