# Generated by Django 5.0.7 on 2024-08-13 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("prime", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="lastname",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
