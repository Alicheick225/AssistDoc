# Generated by Django 5.2.4 on 2025-07-20 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="consultation",
            name="is_validated",
            field=models.BooleanField(default=False),
        ),
    ]
