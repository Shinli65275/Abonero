import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import Q

from apps.businesses.models import Branch, Business


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Administrador"
    SUPERVISOR = "SUPERVISOR", "Supervisor"
    COLLECTOR = "COLLECTOR", "Cobrador"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("El nombre de usuario es obligatorio.")
        username = username.strip().lower()
        email = extra_fields.pop("email", "") or ""
        user = self.model(username=username, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("role", Role.COLLECTOR)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields["role"] = Role.ADMIN
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Usuario del sistema (administrador, supervisor o cobrador).

    Se identifica por nombre de usuario (el correo es opcional porque muchos
    cobradores no lo tienen). El nombre de usuario siempre se guarda en minúsculas.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        "usuario",
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        error_messages={"unique": "Ya existe un usuario con ese nombre."},
    )
    email = models.EmailField("correo electrónico", blank=True)
    first_name = models.CharField("nombres", max_length=100, blank=True)
    last_name = models.CharField("apellidos", max_length=100, blank=True)
    role = models.CharField("rol", max_length=12, choices=Role.choices, default=Role.COLLECTOR)
    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
        verbose_name="empresa",
    )
    is_active = models.BooleanField("activo", default=True)
    is_staff = models.BooleanField("acceso al admin de Django", default=False)
    date_joined = models.DateTimeField("fecha de alta", auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        constraints = [
            models.CheckConstraint(
                condition=Q(role__in=Role.values), name="user_role_valid"
            ),
            # Todo usuario normal pertenece a una empresa; solo el superusuario
            # técnico puede existir antes de crear la empresa.
            models.CheckConstraint(
                condition=Q(is_superuser=True) | Q(business__isnull=False),
                name="user_requires_business_unless_superuser",
            ),
        ]

    def save(self, *args, **kwargs):
        self.username = (self.username or "").strip().lower()
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_short_name(self):
        return self.first_name or self.username

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    # Atajos de rol. Los permisos reales se validan en el backend con estos helpers.
    @property
    def is_admin_role(self):
        return self.is_active and self.role == Role.ADMIN

    @property
    def is_supervisor_role(self):
        return self.is_active and self.role == Role.SUPERVISOR

    @property
    def is_collector_role(self):
        return self.is_active and self.role == Role.COLLECTOR


class EmployeeProfile(models.Model):
    """Datos laborales del usuario (sucursal, teléfono, código de empleado)."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="usuario"
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="employees",
        null=True,
        blank=True,
        verbose_name="sucursal",
    )
    employee_code = models.CharField("código de empleado", max_length=30, blank=True)
    phone = models.CharField("teléfono", max_length=30, blank=True)
    hired_at = models.DateField("fecha de contratación", null=True, blank=True)
    notes = models.TextField("notas", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "perfil de empleado"
        verbose_name_plural = "perfiles de empleados"

    def __str__(self):
        return f"Perfil de {self.user.username}"
