# Generated by Django 5.0.7 on 2024-12-28 23:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("prime", "0013_alter_activity_days_of_week"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActivityExclusion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                (
                    "activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exclusions",
                        to="prime.activity",
                    ),
                ),
            ],
            options={
                "unique_together": {("activity", "date")},
            },
        ),
    ]
