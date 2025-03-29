from django.shortcuts import render, get_object_or_404, redirect
from .models import ExtractionRequest
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q
from .models import (
    ExtractionRequest, 
    ExtractionRequestProcedure, 
    ExtractionRequestDocument,
    OrganizationUnit
)
from .forms import (
    ExtractionRequestForm, 
    ExtractionRequestProcedureForm, 
    ExtractionRequestDocumentForm
)

class ExtractionRequestListView(ListView):
    paginate_by = 10  # Set the number of items per page
    model = ExtractionRequest
    template_name = 'extraction/extraction_request_list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        queryset = ExtractionRequest.objects.all()
        
        # Filtrar por status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtrar por número
        number = self.request.GET.get('number')
        if number:
            procedure_ids = ExtractionRequestProcedure.objects.filter(
                number=number).values_list('extraction_request_id', flat=True)
            document_ids = ExtractionRequestDocument.objects.filter(
                number=number).values_list('extraction_request_id', flat=True)
            queryset = queryset.filter(Q(id__in=procedure_ids) | Q(id__in=document_ids))
        
        # Filtrar por ano
        year = self.request.GET.get('year')
        if year:
            procedure_ids = ExtractionRequestProcedure.objects.filter(
                year=year).values_list('extraction_request_id', flat=True)
            document_ids = ExtractionRequestDocument.objects.filter(
                year=year).values_list('extraction_request_id', flat=True)
            queryset = queryset.filter(Q(id__in=procedure_ids) | Q(id__in=document_ids))
        
        # Filtrar por unidade organizacional
        org_unit = self.request.GET.get('organization_unit')
        if org_unit:
            queryset = queryset.filter(organization_unit_id=org_unit)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ExtractionRequest.EXTRACTION_REQUEST_STATUS_CODES
        context['organization_units'] = OrganizationUnit.objects.all()
        context['filters'] = {
            'status': self.request.GET.get('status', ''),
            'number': self.request.GET.get('number', ''),
            'year': self.request.GET.get('year', ''),
            'organization_unit': self.request.GET.get('organization_unit', ''),
        }
        return context

class ExtractionRequestDetailView(DetailView):
    model = ExtractionRequest
    template_name = 'extraction/extraction_request_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ExtractionRequestForm(instance=self.object)
        context['procedure_form'] = ExtractionRequestProcedureForm()
        context['document_form'] = ExtractionRequestDocumentForm()
        context['procedures'] = self.object.procedures.all()
        context['documents'] = self.object.documents.all()
        context['can_edit'] = self.object.status == ExtractionRequest.STATUS_DRAFT
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status != ExtractionRequest.STATUS_DRAFT:
            messages.error(request, 'Não é possível editar uma solicitação que já foi enviada para análise.')
            return redirect('extraction:request_detail', pk=self.object.pk)

        form = ExtractionRequestForm(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            messages.success(request, 'Solicitação atualizada com sucesso.')
        return self.get(request, *args, **kwargs)

class ExtractionRequestCreateView(CreateView):
    model = ExtractionRequest
    form_class = ExtractionRequestForm
    template_name = 'extraction/extraction_request_form.html'
    success_url = reverse_lazy('extraction:request_list')

    def form_valid(self, form):
        messages.success(self.request, 'Solicitação criada com sucesso.')
        return super().form_valid(form)

def send_to_analysis(request, pk):
    extraction_request = get_object_or_404(ExtractionRequest, pk=pk)
    try:
        extraction_request.send_to_analysis()
        messages.success(request, 'Solicitação enviada para análise com sucesso.')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('extraction:request_detail', pk=pk)

def add_procedure(request, pk):
    if request.method == 'POST':
        extraction_request = get_object_or_404(ExtractionRequest, pk=pk)
        form = ExtractionRequestProcedureForm(request.POST)
        if form.is_valid():
            procedure = form.save(commit=False)
            procedure.extraction_request = extraction_request
            procedure.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'})

def edit_procedure(request, pk, procedure_id):
    if request.method == 'POST':
        procedure = get_object_or_404(ExtractionRequestProcedure, pk=procedure_id)
        form = ExtractionRequestProcedureForm(request.POST, instance=procedure)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'})

def delete_procedure(request, pk, procedure_id):
    if request.method == 'POST':
        procedure = get_object_or_404(ExtractionRequestProcedure, pk=procedure_id)
        procedure.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def add_document(request, pk):
    if request.method == 'POST':
        extraction_request = get_object_or_404(ExtractionRequest, pk=pk)
        form = ExtractionRequestDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.extraction_request = extraction_request
            document.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'})

def edit_document(request, pk, document_id):
    if request.method == 'POST':
        document = get_object_or_404(ExtractionRequestDocument, pk=document_id)
        form = ExtractionRequestDocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'})

def delete_document(request, pk, document_id):
    if request.method == 'POST':
        document = get_object_or_404(ExtractionRequestDocument, pk=document_id)
        document.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def view_request(request, pk):
    request_detail = get_object_or_404(ExtractionRequest, pk=pk)
    context = {
        'request': request_detail,
        'procedures': request_detail.procedures.all(),
        'documents': request_detail.documents.all()
    }
    return render(request, 'extraction/extraction_request_view.html', context)

def review_request(request, pk):
    request_detail = get_object_or_404(ExtractionRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        justification = request.POST.get('justification')
        if action == 'approve':
            request_detail.status = ExtractionRequest.STATUS_APPROVED
            request_detail.justification = justification
        elif action == 'reject':
            request_detail.status = ExtractionRequest.STATUS_REJECTED
            request_detail.justification = justification
        request_detail.save()
        messages.success(request, 'Solicitação atualizada com sucesso.')
        return redirect('extraction:request_list')
    
    return render(request, 'extraction/review_request.html', {'request': request_detail})
