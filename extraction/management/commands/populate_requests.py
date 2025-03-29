from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile
from extraction.models import (
    ExtractionRequest, 
    ExtractionRequestProcedure, 
    ExtractionRequestDocument,
    OrganizationUnit,
    ProcedureType,
    DocumentType
)
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populates the database with sample extraction requests'

    def handle(self, *args, **kwargs):
        # Create Organization Units
        org_units = [
            OrganizationUnit.objects.get_or_create(
                code='SEDE',
                defaults={'name': 'Sede'}
            )[0],
            OrganizationUnit.objects.get_or_create(
                code='FILIAL1',
                defaults={'name': 'Filial São Paulo'}
            )[0],
            OrganizationUnit.objects.get_or_create(
                code='FILIAL2',
                defaults={'name': 'Filial Rio de Janeiro'}
            )[0],
        ]
        self.stdout.write(self.style.SUCCESS('Created organization units'))

        # Create Procedure Types
        procedure_types = [
            ProcedureType.objects.get_or_create(
                code='PROC1',
                defaults={'name': 'Processo Administrativo'}
            )[0],
            ProcedureType.objects.get_or_create(
                code='PROC2',
                defaults={'name': 'Processo Judicial'}
            )[0],
            ProcedureType.objects.get_or_create(
                code='PROC3',
                defaults={'name': 'Inquérito'}
            )[0],
            ProcedureType.objects.get_or_create(
                code='PROC4',
                defaults={'name': 'Sindicância'}
            )[0],
        ]
        self.stdout.write(self.style.SUCCESS('Created procedure types'))

        # Create Document Types
        document_types = [
            DocumentType.objects.get_or_create(
                code='DOC1',
                defaults={'name': 'Ofício'}
            )[0],
            DocumentType.objects.get_or_create(
                code='DOC2',
                defaults={'name': 'Memorando'}
            )[0],
            DocumentType.objects.get_or_create(
                code='DOC3',
                defaults={'name': 'Relatório'}
            )[0],
            DocumentType.objects.get_or_create(
                code='DOC4',
                defaults={'name': 'Parecer'}
            )[0],
        ]
        self.stdout.write(self.style.SUCCESS('Created document types'))

        # Create sample requests
        statuses = ['draft', 'requested', 'approved', 'rejected']
        names = ['João Silva', 'Maria Santos', 'Pedro Oliveira', 'Ana Costa']

        for i in range(100):
            # Create request
            request = ExtractionRequest.objects.create(
                requested_by=random.choice(names),
                request_date=timezone.now() - timedelta(days=random.randint(0, 30)),
                organization_unit=random.choice(org_units),
                status=random.choice(statuses),
                additional_info=f'Informações adicionais da solicitação {i+1}'
            )

            # Add random number of procedures
            for _ in range(random.randint(1, 3)):
                ExtractionRequestProcedure.objects.create(
                    extraction_request=request,
                    procedure_type=random.choice(procedure_types),
                    year=random.randint(2020, 2025),
                    number=random.randint(1, 9999),
                    additional_info=f'Informações do procedimento'
                )

            # Add random number of documents
            for _ in range(random.randint(1, 3)):
                doc = ExtractionRequestDocument.objects.create(
                    extraction_request=request,
                    document_type=random.choice(document_types),
                    year=random.randint(2020, 2025),
                    number=random.randint(1, 9999),
                    additional_info=f'Informações do documento'
                )
                # Create a dummy file for the document
                content = f"Sample content for document {doc.id}".encode('utf-8')
                doc.attached_file.save(
                    f'document_{doc.id}.txt',
                    ContentFile(content),
                    save=True
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated database'))