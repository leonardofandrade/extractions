from django.core.management.base import BaseCommand
from extraction.models import ExtractionRequest, OrganizationUnit
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Popula o banco de dados com 100 solicitações de extração'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        # Obter unidades organizacionais existentes
        organization_units = OrganizationUnit.objects.all()
        
        if not organization_units:
            self.stdout.write(self.style.ERROR('Nenhuma unidade organizacional encontrada.'))
            return
        
        for _ in range(100):
            organization_unit = random.choice(organization_units)
            ExtractionRequest.objects.create(
                request_date=fake.date_time_this_year(),
                requested_by=fake.name(),
                organization_unit=organization_unit,
                status=ExtractionRequest.STATUS_DRAFT,
                additional_info=fake.text(max_nb_chars=200)
            )
        
        self.stdout.write(self.style.SUCCESS('100 solicitações de extração foram criadas com sucesso.'))