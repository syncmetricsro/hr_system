from django.urls import path

from apps.core import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("prihlasenie/", views.login_page, name="login"),
    path("teren/rad/", views.field_queue, name="field_queue"),
    path("healthz/", views.healthz, name="healthz"),
]
