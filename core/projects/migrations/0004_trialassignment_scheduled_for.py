from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0003_readinessrecord_accommodation_na_reason_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="trialassignment",
            name="scheduled_for",
            field=models.DateTimeField(blank=True, null=True, verbose_name="scheduled for"),
        ),
    ]
