from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("intake", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="intakequestion",
            name="transient",
            field=models.BooleanField(default=False, verbose_name="transient"),
        ),
    ]
