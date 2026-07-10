from __future__ import annotations

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    """The four fixed internal roles. No per-user permission matrices (plan §8)."""

    RECRUITER = "recruiter", _("Recruiter")
    COORDINATOR = "coordinator", _("Coordinator")
    MANAGER = "manager", _("Manager/Administrator")
    OBSERVER = "observer", _("Observer")


class UserManager(BaseUserManager):
    """Email-as-username manager."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra):
        if not email:
            raise ValueError("Users must have an email address.")
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
            raise ValueError("Superuser must have is_staff=True.")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    """Internal user identified by email and carrying exactly one fixed role."""

    username = None  # email is the identifier
    email = models.EmailField(_("email"), unique=True)
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=Role.choices,
        default=Role.OBSERVER,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:
        return f"{self.email} ({self.get_role_display()})"


class TotpDevice(models.Model):
    """A user's TOTP authenticator (Stage B4b). One per user; the login flow
    adds a verify step only once ``confirmed``. Secrets are server-side data —
    the admin never displays them (see accounts admin)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="totp_device", verbose_name=_("user"),
    )
    secret = models.CharField(_("secret"), max_length=64)
    confirmed = models.BooleanField(_("confirmed"), default=False)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    confirmed_at = models.DateTimeField(_("confirmed at"), null=True, blank=True)

    class Meta:
        verbose_name = _("TOTP device")
        verbose_name_plural = _("TOTP devices")

    def __str__(self) -> str:
        return f"TOTP for {self.user} ({'confirmed' if self.confirmed else 'pending'})"
