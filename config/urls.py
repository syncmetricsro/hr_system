from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

from apps.accounts import views as account_views
from apps.core import views
from apps.people import views as people_views
from apps.projects import views as project_views

# Routes that must not be language-prefixed.
urlpatterns = [
    path("healthz/", views.healthz, name="healthz"),
    path("i18n/", include("django.conf.urls.i18n")),
]

# Language-prefixed application routes (LocaleMiddleware sets the active language).
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("prihlasenie/", account_views.login_page, name="login"),
    path("odhlasenie/", account_views.logout_view, name="logout"),
    path("teren/rad/", views.field_queue, name="field_queue"),
    path("people/", people_views.people_list, name="people_list"),
    path("people/<int:pk>/", people_views.person_detail, name="person_detail"),
    path("projects/", project_views.project_list, name="project_list"),
    path("projects/<int:pk>/", project_views.project_detail, name="project_detail"),
)
