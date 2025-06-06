# Generated by Django 4.2.20 on 2025-04-12 09:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("actions", "0006_action_is_active_alter_action_thumbnail_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="action",
            name="is_public",
            field=models.BooleanField(default=False, help_text="Is the action public?"),
        ),
    ]
