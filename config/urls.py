from django.apps import apps as django_apps
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path

from core.accounts import views as account_views
from core.audit import views as audit_views
from core.people import views as people_views
from core.projects import views as project_views
from core.ui import exports as core_exports
from core.ui import views
from core.notifications import views as notification_views


def _feature_on(app: str, flag: str) -> bool:
    """A feature mounts its URLs only when installed AND its flag is on."""
    return django_apps.is_installed(f"features.{app}") and getattr(
        settings, "FEATURE_FLAGS", {}
    ).get(flag, True)


# Routes that must not be language-prefixed.
urlpatterns = [
    path("healthz/", views.healthz, name="healthz"),
    path("i18n/setlang/", views.set_language, name="set_language"),
    path("export/people.csv", core_exports.people_csv, name="export_people"),
    path("export/projects.csv", core_exports.projects_csv, name="export_projects"),
]

# Language-prefixed core routes (LocaleMiddleware sets the active language).
app_routes = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("reports/", views.reports, name="reports"),
    path("audit/", audit_views.audit_log, name="audit_log"),
    path("notifications/", notification_views.notification_panel, name="notification_panel"),
    path("notifications/dismiss/", notification_views.notification_dismiss, name="notification_dismiss"),
    path("prihlasenie/", account_views.login_page, name="login"),
    path("odhlasenie/", account_views.logout_view, name="logout"),
    path("2fa/verify/", account_views.two_factor_verify, name="two_factor_verify"),
    path("2fa/setup/", account_views.two_factor_setup, name="two_factor_setup"),
    path("people/", people_views.people_list, name="people_list"),
    path("people/new/", people_views.person_create, name="person_create"),
    path("people/<int:pk>/", people_views.person_detail, name="person_detail"),
    path("people/<int:pk>/edit/", people_views.person_edit, name="person_edit"),
    path("people/<int:person_pk>/archive/", people_views.archive_person, name="archive_person"),
    path("people/<int:person_pk>/recycle/", people_views.recycle_person, name="recycle_person"),
    path("projects/", project_views.project_list, name="project_list"),
    path("projects/<int:pk>/", project_views.project_detail, name="project_detail"),
]

# Trials/readiness stay in core/projects physically (extraction-plan deviation)
# but mount behind their sub-feature flag.
if getattr(settings, "FEATURE_FLAGS", {}).get("recruitment_trials", True):
    app_routes += [
        path("trials/", project_views.trials_queue, name="trials_queue"),
        path("trials/create/", project_views.trial_create, name="trial_create"),
        path("trials/<int:trial_pk>/edit/", project_views.trial_edit, name="trial_edit"),
        path("trials/<int:trial_pk>/outcome/", project_views.trial_outcome, name="trial_outcome"),
        path("people/<int:person_pk>/assign-trial/", project_views.assign_trial, name="assign_trial"),
        path("people/<int:person_pk>/readiness/", project_views.readiness_update, name="readiness_update"),
    ]

# Activation/exit are core assignment workflow.
app_routes += [
    path("people/<int:person_pk>/activate/", project_views.activate_person, name="activate_person"),
    path("people/<int:person_pk>/exit/", project_views.exit_view, name="exit_person"),
]

if _feature_on("logistics", "accommodation"):
    from features.logistics import views as logistics_views

    app_routes += [
        path("accommodation/", logistics_views.accommodation_list, name="accommodation_list"),
        path("accommodation/new/", logistics_views.accommodation_create, name="accommodation_create"),
        path("accommodation/costs/", logistics_views.accommodation_costs, name="accommodation_costs"),
        path("accommodation/<int:pk>/", logistics_views.accommodation_detail, name="accommodation_detail"),
        path("accommodation/<int:pk>/edit/", logistics_views.accommodation_edit, name="accommodation_edit"),
        path("accommodation/<int:accommodation_pk>/rooms/new/", logistics_views.room_create, name="room_create"),
        path("rooms/<int:pk>/edit/", logistics_views.room_edit, name="room_edit"),
        path("rooms/<int:pk>/rate/", logistics_views.set_room_rate_view, name="set_room_rate"),
        path("room-assignments/<int:pk>/rate/", logistics_views.set_assignment_rate_view, name="set_assignment_rate"),
        path("people/<int:person_pk>/assign-room/", logistics_views.assign_room_view, name="assign_room"),
        path("people/<int:person_pk>/release-room/", logistics_views.release_room_view, name="release_room"),
    ]

if _feature_on("logistics", "equipment"):
    from features.logistics import views as logistics_views

    app_routes += [
        path("equipment/catalog/", logistics_views.equipment_catalog, name="equipment_catalog"),
        path("equipment/catalog/new/", logistics_views.equipment_create, name="equipment_create"),
        path("equipment/catalog/<int:pk>/edit/", logistics_views.equipment_edit, name="equipment_edit"),
        path("people/<int:person_pk>/issue-equipment/", logistics_views.issue_equipment_view, name="issue_equipment"),
        path("equipment/<int:issue_pk>/return/", logistics_views.return_equipment_view, name="return_equipment"),
        path("equipment/<int:issue_pk>/flag/", logistics_views.flag_unreturned_view, name="flag_unreturned"),
        path("equipment/reviews/", logistics_views.equipment_reviews, name="equipment_reviews"),
        path("equipment/<int:issue_pk>/review/", logistics_views.review_deduction_view, name="review_deduction"),
    ]

if _feature_on("logistics", "transport"):
    from features.logistics import views as logistics_views

    app_routes += [
        path("projects/<int:project_pk>/transport/", logistics_views.record_transport_view, name="record_transport"),
        path("transport/", logistics_views.transport_trends, name="transport_trends"),
        path("transport/create/", logistics_views.transport_create, name="transport_create"),
        path("transport/<int:pk>/edit/", logistics_views.transport_edit, name="transport_edit"),
    ]

if _feature_on("finance", "profitability"):
    from features.finance import exports as finance_exports
    from features.finance import views as finance_views

    urlpatterns += [
        path("export/finance.csv", finance_exports.finance_csv, name="export_finance"),
    ]
    app_routes += [
        path("finance/", finance_views.finance_summary, name="finance_summary"),
        path("finance/record/", finance_views.record_month, name="finance_record"),
        path("finance/year/<int:year>/", finance_views.finance_year, name="finance_year"),
        path("finance/month/<int:pk>/", finance_views.finance_month_detail, name="finance_month_detail"),
        path("finance/month/<int:pk>/save/", finance_views.finance_month_save, name="finance_month_save"),
        path("finance/month/<int:pk>/lock/", finance_views.finance_month_lock, name="finance_month_lock"),
        path("finance/month/<int:pk>/reopen/", finance_views.finance_month_reopen, name="finance_month_reopen"),
    ]

if _feature_on("intake", "intake"):
    from features.intake import views as intake_views

    app_routes += [
        path("intake/start/", intake_views.intake_start, name="intake_start"),
        path("intake/<int:pk>/", intake_views.intake_panel, name="intake_panel"),
    ]

if _feature_on("messaging", "worker_messaging"):
    from features.messaging import views as messaging_views

    urlpatterns += [
        path("webhooks/twilio/inbound/", messaging_views.twilio_inbound, name="twilio_inbound"),
    ]
    app_routes += [
        path("people/<int:person_pk>/sms/", messaging_views.send_sms_view, name="send_sms"),
    ]

if _feature_on("compliance", "documents"):
    from features.compliance import views as compliance_views

    app_routes += [
        path("compliance/", compliance_views.compliance_list, name="compliance_list"),
    ]

if _feature_on("blacklist", "duplicate_blacklist"):
    from features.blacklist import views as blacklist_views

    app_routes += [
        path("blacklist/", blacklist_views.blacklist_queue, name="blacklist_queue"),
        path("people/<int:person_pk>/blacklist/propose/", blacklist_views.blacklist_propose, name="blacklist_propose"),
        path("blacklist/<int:pk>/decide/", blacklist_views.blacklist_decide, name="blacklist_decide"),
        path("blacklist/<int:pk>/remove/", blacklist_views.blacklist_remove, name="blacklist_remove"),
    ]

if _feature_on("checklists", "checklists"):
    from features.checklists import views as checklist_views

    app_routes += [
        path("checklist/<int:item_pk>/toggle/", checklist_views.toggle_item_view, name="checklist_item_toggle"),
    ]

if _feature_on("advances", "advances"):
    from features.advances import views as advances_views

    urlpatterns += [
        path("export/ledger/thursday.csv", advances_views.thursday_csv, name="ledger_thursday_csv"),
        path("export/ledger/cycle/<int:year>/<int:month>.csv", advances_views.cycle_csv, name="ledger_cycle_csv"),
    ]
    app_routes += [
        path("ledger/", advances_views.ledger_overview, name="ledger_overview"),
        path("ledger/record/", advances_views.ledger_record, name="ledger_record"),
        path("ledger/entry/<int:pk>/action/", advances_views.ledger_entry_action, name="ledger_entry_action"),
        path("ledger/cycle/action/", advances_views.ledger_cycle_action, name="ledger_cycle_action"),
    ]

if _feature_on("payslips", "payslips"):
    from features.payslips import views as payslip_views

    app_routes += [
        path("payslips/", payslip_views.payslip_list, name="payslip_list"),
        path("payslips/<int:pk>/send/", payslip_views.payslip_send, name="payslip_send"),
    ]

if _feature_on("feedback", "feedback"):
    from features.feedback import views as feedback_views

    urlpatterns += [
        path("feedback/<slug:token>/", feedback_views.feedback_form, name="feedback_form"),
    ]
    app_routes += [
        path("feedback/", feedback_views.feedback_inbox, name="feedback_inbox"),
        path("feedback/links/new/", feedback_views.feedback_link_create, name="feedback_link_create"),
    ]

urlpatterns += i18n_patterns(*app_routes)
