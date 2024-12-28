# Generated by Django 5.0.7 on 2024-12-13 03:29

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("prime", "0012_alter_activity_days_of_week"),
    ]

    operations = [
        migrations.AlterField(
            model_name="activity",
            name="days_of_week",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=3), size=7
            ),
        ),
    ]
