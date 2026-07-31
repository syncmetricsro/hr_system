from django.db import migrations, models
import django.db.models.deletion

import core.media


def mark_undated_as_never_expiring(apps, schema_editor):
    Certificate = apps.get_model("compliance", "Certificate")
    Certificate.objects.filter(expiry_date__isnull=True).update(never_expires=True)


def restore_undated_default(apps, schema_editor):
    Certificate = apps.get_model("compliance", "Certificate")
    Certificate.objects.filter(expiry_date__isnull=True).update(never_expires=False)


class Migration(migrations.Migration):
    dependencies = [("compliance", "0002_certificate_category_certificate_document")]

    operations = [
        migrations.RenameField(
            model_name="certificate",
            old_name="document",
            new_name="front_document",
        ),
        migrations.AlterField(
            model_name="certificate",
            name="front_document",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=core.media.certificate_upload_path,
                verbose_name="front or PDF",
            ),
        ),
        migrations.AddField(
            model_name="certificate",
            name="back_document",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=core.media.certificate_upload_path,
                verbose_name="back",
            ),
        ),
        migrations.AddField(
            model_name="certificate",
            name="certificate_number",
            field=models.CharField(
                blank=True, max_length=100, verbose_name="certificate number"
            ),
        ),
        migrations.AddField(
            model_name="certificate",
            name="issuer",
            field=models.CharField(blank=True, max_length=160, verbose_name="issuer"),
        ),
        migrations.AddField(
            model_name="certificate",
            name="never_expires",
            field=models.BooleanField(default=False, verbose_name="does not expire"),
        ),
        migrations.AddField(
            model_name="certificate",
            name="record_status",
            field=models.CharField(
                choices=[
                    ("ACTIVE", "Active"),
                    ("SUPERSEDED", "Superseded"),
                    ("ARCHIVED", "Archived"),
                ],
                default="ACTIVE",
                max_length=20,
                verbose_name="record status",
            ),
        ),
        migrations.AddField(
            model_name="certificate",
            name="supersedes",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="renewed_by",
                to="compliance.certificate",
                verbose_name="supersedes",
            ),
        ),
        migrations.RunPython(mark_undated_as_never_expiring, restore_undated_default),
    ]
