from django.db import migrations


def assign_admin_role(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(is_superuser=True).update(system_role="admin")


def reverse_assign_admin_role(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(system_role="admin").update(
        system_role="user"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_user_system_role"),
    ]

    operations = [
        migrations.RunPython(assign_admin_role, reverse_assign_admin_role),
    ]
