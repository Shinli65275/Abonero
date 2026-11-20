import uuid

from django.db import models


class Business(models.Model):
    """
    La empresa dueña de esta instalación.

    Cada instalación (servidor) atiende a UNA empresa. El modelo existe para
    guardar sus datos y para que el resto de entidades puedan referenciarla,
    sin construir multi-tenencia compleja.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("nombre comercial", max_length=150)
    legal_name = models.CharField("razón social", max_length=200, blank=True)
    tax_id = models.CharField("RFC", max_length=20, blank=True)
    phone = models.CharField("teléfono", max_length=30, blank=True)
    address = models.CharField("dirección", max_length=255, blank=True)
    currency = models.CharField("moneda", max_length=3, default="MXN")
    is_active = models.BooleanField("activa", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "empresa"
        verbose_name_plural = "empresas"

    def __str__(self):
        return self.name


class Branch(models.Model):
    """Sucursal u oficina de la empresa."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business, on_delete=models.PROTECT, related_name="branches", verbose_name="empresa"
    )
    name = models.CharField("nombre", max_length=150)
    address = models.CharField("dirección", max_length=255, blank=True)
    phone = models.CharField("teléfono", max_length=30, blank=True)
    is_active = models.BooleanField("activa", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "sucursal"
        verbose_name_plural = "sucursales"
        constraints = [
            models.UniqueConstraint(
                fields=["business", "name"], name="unique_branch_name_per_business"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.business.name})"
