from django.db import migrations, models
import django.db.models.deletion

def set_default_organization_unit(apps, schema_editor):
    ExtractionRequest = apps.get_model('extraction', 'ExtractionRequest')
    OrganizationUnit = apps.get_model('extraction', 'OrganizationUnit')
    
    # Get or create a default organization unit
    default_unit, created = OrganizationUnit.objects.get_or_create(
        code='SEDE',
        defaults={'name': 'Sede'}
    )
    
    # Update all requests that have null organization_unit
    ExtractionRequest.objects.filter(organization_unit__isnull=True).update(
        organization_unit=default_unit
    )

class Migration(migrations.Migration):

    dependencies = [
        ('extraction', '0005_extractionrequest_justification'),
    ]

    operations = [
        migrations.RunPython(set_default_organization_unit),
        migrations.AlterField(
            model_name='extractionrequest',
            name='organization_unit',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='extraction_requests',
                to='extraction.organizationunit',
                verbose_name='Unidade Organizacional'
            ),
        ),
    ]
