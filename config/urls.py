from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

from apps.accounts import views as account_views
from apps.compliance import views as compliance_views
from apps.core import exports as core_exports
from apps.core import views
from apps.finance import views as finance_views
from apps.intake import views as intake_views
from apps.logistics import views as logistics_views
from apps.messaging import views as messaging_views
from apps.people import views as people_views
from apps.projects import views as project_views

# Routes that must not be language-prefixed.
urlpatterns = [
    path("healthz/", views.healthz, name="healthz"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("export/people.csv", core_exports.people_csv, name="export_people"),
    path("export/projects.csv", core_exports.projects_csv, name="export_projects"),
    path("export/finance.csv", core_exports.finance_csv, name="export_finance"),
    path("webhooks/twilio/inbound/", messaging_views.twilio_inbound, name="twilio_inbound"),
]

# Language-prefixed application routes (LocaleMiddleware sets the active language).
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("prihlasenie/", account_views.login_page, name="login"),
    path("odhlasenie/", account_views.logout_view, name="logout"),
    path("people/", people_views.people_list, name="people_list"),
    path("people/new/", people_views.person_create, name="person_create"),
    path("people/<int:pk>/", people_views.person_detail, name="person_detail"),
    path("projects/", project_views.project_list, name="project_list"),
    path("projects/<int:pk>/", project_views.project_detail, name="project_detail"),
    path("trials/", project_views.trials_queue, name="trials_queue"),
    path("trials/<int:trial_pk>/outcome/", project_views.trial_outcome, name="trial_outcome"),
    path("people/<int:person_pk>/assign-trial/", project_views.assign_trial, name="assign_trial"),
    path("people/<int:person_pk>/readiness/", project_views.readiness_update, name="readiness_update"),
    path("people/<int:person_pk>/activate/", project_views.activate_person, name="activate_person"),
    path("people/<int:person_pk>/exit/", project_views.exit_view, name="exit_person"),
    path("accommodation/", logistics_views.accommodation_list, name="accommodation_list"),
    path("accommodation/<int:pk>/", logistics_views.accommodation_detail, name="accommodation_detail"),
    path("people/<int:person_pk>/assign-room/", logistics_views.assign_room_view, name="assign_room"),
    path("people/<int:person_pk>/release-room/", logistics_views.release_room_view, name="release_room"),
    path("people/<int:person_pk>/issue-equipment/", logistics_views.issue_equipment_view, name="issue_equipment"),
    path("equipment/<int:issue_pk>/return/", logistics_views.return_equipment_view, name="return_equipment"),
    path("projects/<int:project_pk>/transport/", logistics_views.record_transport_view, name="record_transport"),
    path("finance/", finance_views.finance_summary, name="finance_summary"),
    path("finance/record/", finance_views.record_month, name="finance_record"),
    path("intake/start/", intake_views.intake_start, name="intake_start"),
    path("intake/<int:pk>/", intake_views.intake_panel, name="intake_panel"),
    path("people/<int:person_pk>/sms/", messaging_views.send_sms_view, name="send_sms"),
    path("compliance/", compliance_views.compliance_list, name="compliance_list"),
)
