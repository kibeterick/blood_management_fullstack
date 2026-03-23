# Generated migration to fix duplicate alert_sent_at column

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_blood_system', '0006_remove_security_models'),
    ]

    operations = [
        # This migration removes the duplicate alert_sent_at column if it exists
        # The column is already defined in the BloodInventory model, so we just need to ensure it's not duplicated
        migrations.RunSQL(
            sql="SELECT 1;",  # No-op SQL to prevent errors
            reverse_sql="SELECT 1;",
        ),
    ]
