from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class OrganizationUnit(models.Model):
    name = models.CharField('Nome', max_length=100)
    code = models.CharField('Código', max_length=20, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                             related_name='children', verbose_name='Unidade Superior')
    
    def __str__(self):
        return f'{self.code} - {self.name}'

    class Meta:
        verbose_name = 'Unidade Organizacional'
        verbose_name_plural = 'Unidades Organizacionais'

class ProcedureType(models.Model):
    name = models.CharField('Nome', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Procedimento'
        verbose_name_plural = 'Tipos de Procedimentos'

class DocumentType(models.Model):
    name = models.CharField('Nome', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documentos'

class ExtractionRequest(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_REQUESTED = 'requested'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_SUCCESS = 'success'

    EXTRACTION_REQUEST_STATUS_CODES = [
        (STATUS_DRAFT, 'Pendente de Envio'),
        (STATUS_REQUESTED, 'Solicitada'),
        (STATUS_APPROVED, 'Aprovada'),
        (STATUS_REJECTED, 'Rejeitada'),
        (STATUS_IN_PROGRESS, 'Em Andamento'),
        (STATUS_COMPLETED, 'Finalizada'),
        (STATUS_FAILED, 'Finalizada - Falhou'),
        (STATUS_SUCCESS, 'Finalizada - Sucesso'),
    ]

    request_date = models.DateTimeField('Data da Solicitação', default=timezone.now)
    requested_by = models.CharField('Solicitado por', max_length=100)
    organization_unit = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.PROTECT,
        verbose_name='Unidade Organizacional',
        related_name='extraction_requests',
        null=True,
        blank=True
    )
    status = models.CharField(
        'Status',
        max_length=20,
        choices=EXTRACTION_REQUEST_STATUS_CODES,
        default=STATUS_DRAFT,
        editable=False
    )
    additional_info = models.TextField('Informações Adicionais', blank=True, null=True)
    justification = models.TextField('Justificativa da Decisão', blank=True, null=True)

    def __str__(self):
        return f'Solicitação #{self.id} - {self.requested_by} ({self.organization_unit.code if self.organization_unit else "N/A"})'

    class Meta:
        verbose_name = 'Solicitação de Extração'
        verbose_name_plural = 'Solicitações de Extração'

    def send_to_analysis(self):
        """Envia a solicitação para análise"""
        if self.status != self.STATUS_DRAFT:
            raise ValidationError('Apenas solicitações pendentes podem ser enviadas para análise.')
        
        if not self.organization_unit:
            raise ValidationError('A unidade organizacional é obrigatória para enviar a solicitação.')
        
        if not (self.procedures.exists() or self.documents.exists()):
            raise ValidationError('A solicitação deve ter pelo menos um procedimento ou documento.')
        
        self.status = self.STATUS_REQUESTED
        self.save()

    def can_be_sent_to_analysis(self):
        """Verifica se a solicitação pode ser enviada para análise"""
        return (
            self.status == self.STATUS_DRAFT and 
            self.organization_unit is not None and
            (self.procedures.exists() or self.documents.exists())
        )

class ExtractionRequestProcedure(models.Model):
    extraction_request = models.ForeignKey(
        ExtractionRequest,
        on_delete=models.CASCADE,
        related_name='procedures',
        verbose_name='Solicitação de Extração'
    )
    procedure_type = models.ForeignKey(
        ProcedureType,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Procedimento'
    )
    year = models.IntegerField('Ano')
    number = models.IntegerField('Número')
    additional_info = models.TextField('Informações Adicionais', blank=True, null=True)

    def __str__(self):
        return f'Procedimento {self.procedure_type} - {self.number}/{self.year}'

    class Meta:
        verbose_name = 'Procedimento da Solicitação'
        verbose_name_plural = 'Procedimentos da Solicitação'

class ExtractionRequestDocument(models.Model):
    extraction_request = models.ForeignKey(
        ExtractionRequest,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Solicitação de Extração'
    )
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Documento'
    )
    year = models.IntegerField('Ano')
    number = models.IntegerField('Número')
    attached_file = models.FileField('Arquivo Anexo', upload_to='documents/')
    additional_info = models.TextField('Informações Adicionais', blank=True, null=True)

    def __str__(self):
        return f'Documento {self.document_type} - {self.number}/{self.year}'

    class Meta:
        verbose_name = 'Documento da Solicitação'
        verbose_name_plural = 'Documentos da Solicitação'
