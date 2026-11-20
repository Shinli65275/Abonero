from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.businesses.models import Branch, Business


class Command(BaseCommand):
    help = (
        "Crea la empresa de esta instalación y su sucursal principal. "
        "Es idempotente: si ya existe una empresa, no crea otra."
    )

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True, help="Nombre comercial de la empresa")
        parser.add_argument("--branch", default="Matriz", help="Nombre de la sucursal principal")

    @transaction.atomic
    def handle(self, *args, **options):
        if Business.objects.exists():
            business = Business.objects.first()
            self.stdout.write(self.style.WARNING(f"Ya existe la empresa '{business}'. No se creó otra."))
            return
        name = options["name"].strip()
        if not name:
            raise CommandError("El nombre no puede estar vacío.")
        business = Business.objects.create(name=name)
        Branch.objects.create(business=business, name=options["branch"].strip() or "Matriz")
        self.stdout.write(self.style.SUCCESS(f"Empresa '{business}' creada con su sucursal principal."))
