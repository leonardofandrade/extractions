from django.contrib import admin
from .models import (
    OrganizationUnit,
    ProcedureType,
    DocumentType,
    ExtractionRequest,
    ExtractionRequestProcedure,
    ExtractionRequestDocument
)

@admin.register(OrganizationUnit)
class OrganizationUnitAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent')
    search_fields = ('code', 'name')
    list_filter = ('parent',)

@admin.register(ProcedureType)
class ProcedureTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ExtractionRequestProcedureInline(admin.TabularInline):
    model = ExtractionRequestProcedure
    extra = 1

class ExtractionRequestDocumentInline(admin.TabularInline):
    model = ExtractionRequestDocument
    extra = 1

@admin.register(ExtractionRequest)
class ExtractionRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_date', 'requested_by', 'organization_unit', 'get_status_display')
    list_filter = ('request_date', 'organization_unit', 'status')
    search_fields = ('requested_by', 'organization_unit__name', 'organization_unit__code')
    readonly_fields = ('status',)
    inlines = [ExtractionRequestProcedureInline, ExtractionRequestDocumentInline]

    def get_status_display(self, obj):
        return dict(obj.EXTRACTION_REQUEST_STATUS_CODES).get(obj.status)
    get_status_display.short_description = 'Status'
