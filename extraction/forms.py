from django import forms
from .models import ExtractionRequest, ExtractionRequestProcedure, ExtractionRequestDocument

class ExtractionRequestForm(forms.ModelForm):
    class Meta:
        model = ExtractionRequest
        fields = ['requested_by', 'organization_unit', 'additional_info']
        widgets = {
            'requested_by': forms.TextInput(attrs={'class': 'form-control'}),
            'organization_unit': forms.Select(attrs={
                'class': 'form-control select2',
                'required': True
            }),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ExtractionRequestProcedureForm(forms.ModelForm):
    class Meta:
        model = ExtractionRequestProcedure
        fields = ['procedure_type', 'year', 'number', 'additional_info']
        widgets = {
            'procedure_type': forms.Select(attrs={'class': 'form-control select2'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ExtractionRequestDocumentForm(forms.ModelForm):
    class Meta:
        model = ExtractionRequestDocument
        fields = ['document_type', 'year', 'number', 'attached_file', 'additional_info']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control select2'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'attached_file': forms.FileInput(attrs={'class': 'form-control'}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }