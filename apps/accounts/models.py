from __future__ import annotations

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    """The four fixed internal roles. No per-user permission matrices (plan §8)."""

    RECRUITER = "recruiter", _("Náborár")
    COORDINATOR = "coordinator", _("Koordinátor")
    MANAGER = "manager", _("Manažér/Administrátor")
    OBSERVER = "observer", _("Pozorovateľ")


class UserManager(BaseUserManager):
    """Email-as-username manager."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra):
        if not email:
            raise ValueError("Používateľ musí mať e-mail.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        extra.setdefault("role", Role.OBSERVER)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", Role.MANAGER)
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser musí mať is_staff=True.")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser musí mať is_superuser=True.")
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    """Internal user identified by email and carrying exactly one fixed role."""

    username = None  # email is the identifier
    email = models.EmailField(_("e-mail"), unique=True)
    role = models.CharField(
        _("rola"),
        max_length=20,
        choices=Role.choices,
        default=Role.OBSERVER,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("používateľ")
        verbose_name_plural = _("používatelia")

    def __str__(self) -> str:
        return f"{self.email} ({self.get_role_display()})"
