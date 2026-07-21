import django.utils.timezone
from django.db import migrations, models


def local_issue_date(created_at):
    return django.utils.timezone.localtime(created_at).date()


def backfill_issue_dates(apps, schema_editor):
    Payslip = apps.get_model("payslips", "Payslip")
    pending = []
    for payslip in Payslip.objects.filter(issue_date__isnull=True).iterator():
        payslip.issue_date = local_issue_date(payslip.created_at)
        pending.append(payslip)
        if len(pending) == 500:
            Payslip.objects.bulk_update(pending, ["issue_date"])
            pending.clear()
    if pending:
        Payslip.objects.bulk_update(pending, ["issue_date"])


class Migration(migrations.Migration):
    dependencies = [("payslips", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="payslip",
            name="issue_date",
            field=models.DateField(null=True, verbose_name="issue date"),
        ),
        migrations.RunPython(backfill_issue_dates, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="payslip",
            name="issue_date",
            field=models.DateField(
                default=django.utils.timezone.localdate,
                verbose_name="issue date",
            ),
        ),
    ]
