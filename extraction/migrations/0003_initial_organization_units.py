from django.db import migrations

def create_initial_organization_units(apps, schema_editor):
    OrganizationUnit = apps.get_model('extraction', 'OrganizationUnit')
    
    # Criar unidade principal
    sede = OrganizationUnit.objects.create(
        name='Sede',
        code='SEDE'
    )
    
    # Criar departamentos
    departamentos = [
        ('DTIC', 'Departamento de Tecnologia da Informação'),
        ('DADM', 'Departamento Administrativo'),
        ('DJUR', 'Departamento Jurídico')
    ]
    
    for code, name in departamentos:
        OrganizationUnit.objects.create(
            name=name,
            code=code,
            parent=sede
        )

def remove_initial_organization_units(apps, schema_editor):
    OrganizationUnit = apps.get_model('extraction', 'OrganizationUnit')
    OrganizationUnit.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('extraction', '0002_organizationunit_extractionrequest_organization_unit'),
    ]

    operations = [
        migrations.RunPython(
            create_initial_organization_units,
            remove_initial_organization_units
        ),
    ]