from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("logistics", "0007_alter_equipmentissue_charge_amount_and_more")]

    operations = [
        migrations.AddField(
            model_name="room",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="active"),
        ),
        migrations.AddConstraint(
            model_name="room",
            constraint=models.UniqueConstraint(
                fields=("accommodation", "label"),
                name="unique_room_label_per_accommodation",
            ),
        ),
    ]
